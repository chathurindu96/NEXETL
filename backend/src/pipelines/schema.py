"""Logical schema propagation for Pipeline graph nodes."""

from __future__ import annotations

from copy import deepcopy


Schema = list[dict[str, object]]


def normalize_schema(value: object) -> Schema:
    if not isinstance(value, list): return []
    result=[]
    for ordinal,item in enumerate(value,1):
        if not isinstance(item,dict) or not isinstance(item.get("name"),str): continue
        result.append({"name":item["name"],"logicalType":item.get("logicalType","unknown"),"nativeType":item.get("nativeType"),"nullable":bool(item.get("nullable",True)),"ordinal":ordinal,"metadata":item.get("metadata",{})})
    return result


def infer_schema(kind: str, configuration: dict[str, object], inputs: dict[str, list[Schema]]) -> Schema:
    incoming=[schema for values in inputs.values() for schema in values]
    base=deepcopy(incoming[0]) if incoming else normalize_schema(configuration.get("schemaFields",[]))
    if kind in {"database_source","sql_query_source"}: return normalize_schema(configuration.get("schemaFields",base))
    if kind=="select_columns":
        by_name={field["name"]:field for field in base}; return [deepcopy(by_name[name]) for name in configuration.get("columns",[]) if name in by_name]
    if kind=="rename_columns":
        mapping={str(item.get("from")):str(item.get("to")) for item in configuration.get("mappings",[]) if isinstance(item,dict)}
        for field in base: field["name"]=mapping.get(str(field["name"]),field["name"])
    elif kind=="cast":
        casts={str(item.get("column")):str(item.get("type")) for item in configuration.get("casts",[]) if isinstance(item,dict)}
        for field in base:
            if field["name"] in casts: field["logicalType"]=casts[field["name"]]; field["nativeType"]=None
    elif kind=="derived_column":
        base=[field for field in base if field["name"]!=configuration.get("column")]
        base.append({"name":configuration.get("column"),"logicalType":configuration.get("outputType","unknown"),"nativeType":None,"nullable":True,"ordinal":len(base)+1,"metadata":{"derived":True}})
    elif kind=="aggregate":
        by_name={field["name"]:field for field in base}; output=[]
        for name in configuration.get("groupBy",[]):
            if name in by_name: output.append(deepcopy(by_name[name]))
        for item in configuration.get("aggregates",[]):
            if isinstance(item,dict): output.append({"name":item.get("as") or f"{str(item.get('function','count')).lower()}_{item.get('column','rows')}","logicalType":"integer" if str(item.get("function")).upper()=="COUNT" else "decimal","nativeType":None,"nullable":False,"ordinal":len(output)+1,"metadata":{"aggregate":item.get("function")}})
        base=output
    elif kind in {"join","lookup"}:
        left=deepcopy((inputs.get("left") or inputs.get("primary") or [[]])[0]); right=deepcopy((inputs.get("right") or inputs.get("lookup") or [[]])[0]); used={field["name"] for field in left}
        for field in right:
            if field["name"] in used: field["name"]=f"right_{field['name']}"
        base=left+right
    elif kind=="union":
        base=deepcopy(incoming[0]) if incoming else []
    for ordinal,field in enumerate(base,1): field["ordinal"]=ordinal
    return base


def schema_issues(kind: str, configuration: dict[str, object], inputs: dict[str, list[Schema]], output: Schema) -> list[dict[str, object]]:
    issues=[]; names=[str(field["name"]) for field in output]
    if len(names)!=len(set(names)): issues.append({"code":"NEXETL_SCHEMA_DUPLICATE_COLUMN","severity":"ERROR","message":"The output schema contains duplicate column names.","field":"configuration"})
    if kind=="union":
        schemas=[schema for values in inputs.values() for schema in values]
        for schema in schemas[1:]:
            if [(f["name"],f["logicalType"]) for f in schema] != [(f["name"],f["logicalType"]) for f in schemas[0]]: issues.append({"code":"NEXETL_SCHEMA_UNION_MISMATCH","severity":"ERROR","message":"Union inputs must have matching names and compatible types."}); break
    if kind=="database_target":
        target=normalize_schema(configuration.get("targetSchema",[])); target_names={f["name"] for f in target}; mappings=configuration.get("mappings",[])
        for item in mappings if isinstance(mappings,list) else []:
            if isinstance(item,dict) and item.get("target") not in target_names: issues.append({"code":"NEXETL_TARGET_COLUMN_MISSING","severity":"ERROR","message":f"Target column '{item.get('target')}' does not exist.","field":"mappings"})
    return issues
