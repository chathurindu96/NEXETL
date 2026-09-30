"""Node executor strategies over bounded row batches."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

from django.conf import settings

from pipelines.connections import ADAPTERS, LocalEncryptedSecretProvider
from pipelines.infrastructure.persistence.models import ConnectionRecord, PipelineVersionNodeRecord
from pipelines.runtime.expressions import evaluate, predicate
from pipelines.runtime.spool import SpoolStore


@dataclass
class ExecutionContext:
    spool: SpoolStore
    incoming: dict[str,list[tuple[str,str]]]
    cancelled: Callable[[],bool]
    warn: Callable[[str,str],None]


def _input_batches(context:ExecutionContext,port:str="input"):
    for source,source_port in context.incoming.get(port,[]): yield from context.spool.batches(source,source_port)


def _write_batches(node_id:str,context:ExecutionContext,transform,port="output"):
    read=written=batches=0
    for batch in _input_batches(context):
        if context.cancelled(): raise InterruptedError("Cancellation requested.")
        read+=len(batch); output=transform(batch)
        if output: context.spool.write(node_id,output,port); written+=len(output); batches+=1
    return {"inputRows":read,"outputRows":written,"batchCount":batches}


def _connection(configuration:dict[str,object]):
    record=ConnectionRecord.objects.get(id=UUID(str(configuration["connectionId"])),state="ENABLED")
    if not record.secret_id: raise RuntimeError("NEXETL_CONNECTION_SECRET_UNAVAILABLE")
    return record,ADAPTERS[record.connector_key],LocalEncryptedSecretProvider().resolve(record.secret_id)


def _cast(value:Any,target:str,on_failure:str):
    if value is None:return None
    try:
        if target=="string":return str(value)
        if target=="integer":return int(value)
        if target=="decimal":return float(Decimal(str(value)))
        if target=="boolean":
            if isinstance(value,bool):return value
            normalized=str(value).lower()
            if normalized in {"true","1","yes"}:return True
            if normalized in {"false","0","no"}:return False
            raise ValueError()
        if target=="date":return date.fromisoformat(str(value)).isoformat()
        if target=="timestamp":return datetime.fromisoformat(str(value)).isoformat()
    except (ValueError,TypeError,ArithmeticError):
        if on_failure=="NULL":return None
        raise RuntimeError("NEXETL_CAST_FAILED")
    raise RuntimeError("NEXETL_CAST_TYPE_UNSUPPORTED")


def execute_node(node:PipelineVersionNodeRecord,context:ExecutionContext)->dict[str,int]:
    node_id=str(node.design_node_id); kind=node.kind; config=node.configuration
    if kind in {"database_source","sql_query_source"}:
        record,adapter,password=_connection(config); source={**config,"dataset":config.get("dataset"),"query":config.get("query")}; rows=batches=0
        for batch in adapter.read_batches(record.configuration,password,source,int(config.get("batchSize",settings.CONFIGURATION.runtime.batch_size)),settings.CONFIGURATION.runtime.operation_timeout_seconds):
            if context.cancelled():raise InterruptedError("Cancellation requested.")
            context.spool.write(node_id,batch); rows+=len(batch); batches+=1
        return {"inputRows":0,"outputRows":rows,"batchCount":batches}
    if kind=="select_columns":
        columns=[str(value) for value in config.get("columns",[])]; return _write_batches(node_id,context,lambda batch:[{column:row.get(column) for column in columns} for row in batch])
    if kind=="rename_columns":
        mapping={str(item["from"]):str(item["to"]) for item in config.get("mappings",[]) if isinstance(item,dict)}
        return _write_batches(node_id,context,lambda batch:[{mapping.get(key,key):value for key,value in row.items()} for row in batch])
    if kind=="filter": return _write_batches(node_id,context,lambda batch:[row for row in batch if predicate(config["predicate"],row)])
    if kind=="derived_column":
        def derived(batch):
            result=[]
            for row in batch: updated=dict(row); updated[str(config["column"])]=evaluate(str(config["expression"]),row); result.append(updated)
            return result
        return _write_batches(node_id,context,derived)
    if kind=="cast":
        casts={str(item["column"]):(str(item["type"]),str(item.get("onFailure","FAIL"))) for item in config.get("casts",[]) if isinstance(item,dict)}
        def convert(batch):
            result=[]
            for row in batch:
                updated=dict(row)
                for column,(target,behavior) in casts.items():updated[column]=_cast(updated.get(column),target,behavior)
                result.append(updated)
            return result
        return _write_batches(node_id,context,convert)
    if kind in {"limit_sample","null_handling"}:
        remaining=int(config.get("limit",0)) if kind=="limit_sample" else None
        def adjust(batch):
            nonlocal remaining
            if kind=="limit_sample": output=batch[:max(remaining,0)]; remaining-=len(output); return output
            rules={str(item["column"]):item for item in config.get("rules",[]) if isinstance(item,dict)}; output=[]
            for row in batch:
                updated=dict(row)
                for column,rule in rules.items():
                    if updated.get(column) is None and rule.get("action")=="REPLACE":updated[column]=rule.get("value")
                    if updated.get(column) is None and rule.get("action")=="REJECT":break
                else:output.append(updated)
            return output
        return _write_batches(node_id,context,adjust)
    if kind in {"distinct","deduplicate"}:
        keys=[str(v) for v in config.get("keys",[])] if kind=="deduplicate" else []; seen=set()
        def unique(batch):
            output=[]
            for row in batch:
                marker=tuple(row.get(key) for key in keys) if keys else tuple(sorted(row.items()))
                if marker not in seen:seen.add(marker); output.append(row)
            return output
        return _write_batches(node_id,context,unique)
    if kind=="sort":
        rows=[row for batch in _input_batches(context) for row in batch]; columns=config.get("columns",[])
        for item in reversed(columns):
            if isinstance(item,dict): rows.sort(key=lambda row:(row.get(str(item.get("column"))) is None,row.get(str(item.get("column")))),reverse=str(item.get("direction","ASC")).upper()=="DESC")
        for start in range(0,len(rows),context.spool.batch_size):context.spool.write(node_id,rows[start:start+context.spool.batch_size])
        return {"inputRows":len(rows),"outputRows":len(rows),"batchCount":max(1,(len(rows)+context.spool.batch_size-1)//context.spool.batch_size)}
    if kind=="aggregate":
        group_by=[str(v) for v in config.get("groupBy",[])]; groups={}
        count=0
        for batch in _input_batches(context):
            for row in batch:
                count+=1; key=tuple(row.get(name) for name in group_by); state=groups.setdefault(key,{"__count":0}); state["__count"]+=1
                for item in config.get("aggregates",[]):
                    if not isinstance(item,dict):continue
                    function=str(item.get("function","COUNT")).upper(); column=str(item.get("column","")); alias=str(item.get("as") or f"{function.lower()}_{column or 'rows'}"); value=row.get(column)
                    if function=="COUNT":state[alias]=state.get(alias,0)+1
                    elif value is not None:
                        if function in {"SUM","AVG"}:state[alias]=state.get(alias,0)+float(value); state[f"__{alias}_count"]=state.get(f"__{alias}_count",0)+1
                        elif function=="MIN":state[alias]=value if alias not in state else min(state[alias],value)
                        elif function=="MAX":state[alias]=value if alias not in state else max(state[alias],value)
        output=[]
        for key,state in groups.items():
            row=dict(zip(group_by,key,strict=True))
            for item in config.get("aggregates",[]):
                function=str(item.get("function","COUNT")).upper(); alias=str(item.get("as") or f"{function.lower()}_{item.get('column','rows')}"); row[alias]=state.get(alias,0); row[alias]=row[alias]/state.get(f"__{alias}_count",1) if function=="AVG" else row[alias]
            output.append(row)
        for start in range(0,len(output),context.spool.batch_size):context.spool.write(node_id,output[start:start+context.spool.batch_size])
        return {"inputRows":count,"outputRows":len(output),"batchCount":max(1,(len(output)+context.spool.batch_size-1)//context.spool.batch_size)}
    if kind in {"join","lookup"}:
        left_port="left" if kind=="join" else "primary"; right_port="right" if kind=="join" else "lookup"; left=[row for source,port in context.incoming.get(left_port,[]) for batch in context.spool.batches(source,port) for row in batch]; right=[row for source,port in context.incoming.get(right_port,[]) for batch in context.spool.batches(source,port) for row in batch]; keys=config.get("keys",[]); index=defaultdict(list)
        for right_index,row in enumerate(right):index[tuple(row.get(str(item.get("right"))) for item in keys)].append((right_index,row))
        output=[]; join_type=str(config.get("joinType","LEFT" if kind=="lookup" else "INNER")).upper()
        matched_right=set()
        for left_row in left:
            matches=index.get(tuple(left_row.get(str(item.get("left"))) for item in keys),[])
            if not matches and join_type in {"LEFT","FULL"}:output.append(dict(left_row))
            for right_index,right_row in matches:
                matched_right.add(right_index)
                merged=dict(left_row)
                for key,value in right_row.items():merged[key if key not in merged else f"right_{key}"]=value
                output.append(merged)
        if join_type in {"RIGHT","FULL"}:
            left_columns=list(left[0]) if left else []
            for right_index,right_row in enumerate(right):
                if right_index in matched_right:continue
                merged={column:None for column in left_columns}
                for key,value in right_row.items():merged[key if key not in merged else f"right_{key}"]=value
                output.append(merged)
        for start in range(0,len(output),context.spool.batch_size):context.spool.write(node_id,output[start:start+context.spool.batch_size])
        return {"inputRows":len(left)+len(right),"outputRows":len(output),"batchCount":max(1,(len(output)+context.spool.batch_size-1)//context.spool.batch_size)}
    if kind=="union":
        total=batches=0
        for sources in context.incoming.values():
            for source,port in sources:
                for batch in context.spool.batches(source,port):context.spool.write(node_id,batch); total+=len(batch); batches+=1
        return {"inputRows":total,"outputRows":total,"batchCount":batches}
    if kind=="split_router":
        total=0
        for batch in _input_batches(context):
            routed=defaultdict(list)
            for row in batch:
                total+=1
                for route in config.get("routes",[]):
                    if isinstance(route,dict) and predicate(route.get("predicate",{}),row):routed[str(route.get("key","matched"))].append(row); break
            for port,rows in routed.items():context.spool.write(node_id,rows,port)
        return {"inputRows":total,"outputRows":total,"batchCount":0}
    if kind in {"data_quality","validation_gate"}:
        rules=config.get("rules",[]); action=str(config.get("action","FAIL_PIPELINE")); rejected=0
        def quality(batch):
            nonlocal rejected
            output=[]
            for row in batch:
                valid=True
                for rule in rules:
                    if not isinstance(rule,dict):continue
                    value=row.get(str(rule.get("column"))); check=rule.get("type")
                    if check=="not_null" and value is None:valid=False
                    if check=="range" and value is not None and not float(rule.get("min",value))<=float(value)<=float(rule.get("max",value)):valid=False
                    if check=="allowed_values" and value not in rule.get("values",[]):valid=False
                if valid:output.append(row)
                else:
                    rejected+=1
                    if action=="ROUTE_INVALID":context.spool.write(node_id,[row],"invalid")
            return output
        metrics=_write_batches(node_id,context,quality); metrics["rejectedRows"]=rejected
        if rejected and action=="FAIL_PIPELINE":raise RuntimeError("NEXETL_DATA_QUALITY_FAILED")
        if rejected and action=="WARN":context.warn("NEXETL_DATA_QUALITY_WARNING",f"{rejected} rows failed quality rules.")
        return metrics
    if kind=="database_target":
        record,adapter,password=_connection(config); mappings=config.get("mappings",[])
        def mapped():
            for batch in _input_batches(context):
                if mappings:yield [{str(item["target"]):row.get(str(item["input"])) for item in mappings if isinstance(item,dict)} for row in batch]
                else:yield batch
        input_rows=sum(context.spool.count(source,port) for source,port in context.incoming.get("input",[])); result=adapter.write_batches(record.configuration,password,config,mapped(),settings.CONFIGURATION.runtime.operation_timeout_seconds); return {"inputRows":input_rows,"outputRows":int(result.get("rowsWritten",0)),"batchCount":max(1,(input_rows+context.spool.batch_size-1)//context.spool.batch_size)}
    raise RuntimeError("NEXETL_NODE_EXECUTOR_UNAVAILABLE")
