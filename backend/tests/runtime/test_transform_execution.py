"""Execution acceptance for batch and stateful transforms."""

from types import SimpleNamespace
from uuid import uuid4

from pipelines.runtime.executors import ExecutionContext,execute_node
from pipelines.runtime.spool import SpoolStore


def _node(kind,configuration):return SimpleNamespace(design_node_id=uuid4(),kind=kind,configuration=configuration)


def test_batch_transform_chain_executes_real_rows():
    with SpoolStore(2,100) as spool:
        spool.write("source",[{"name":" Ada ","age":"21","active":True},{"name":"Bob","age":"17","active":False}])
        context=ExecutionContext(spool,{"input":[("source","output")]},lambda:False,lambda *_:None)
        selected=_node("select_columns",{"columns":["name","age","active"]});execute_node(selected,context)
        filtered=_node("filter",{"predicate":{"column":"active","operator":"=","value":True}});execute_node(filtered,ExecutionContext(spool,{"input":[(str(selected.design_node_id),"output")]},lambda:False,lambda *_:None))
        derived=_node("derived_column",{"column":"clean_name","expression":"trim(name)","outputType":"string"});metrics=execute_node(derived,ExecutionContext(spool,{"input":[(str(filtered.design_node_id),"output")]},lambda:False,lambda *_:None))
        assert metrics["outputRows"]==1 and spool.all(str(derived.design_node_id))==[{"name":" Ada ","age":"21","active":True,"clean_name":"Ada"}]


def test_full_join_outputs_unmatched_rows_from_both_sides():
    with SpoolStore(2,100) as spool:
        spool.write("left",[{"id":1,"name":"A"},{"id":2,"name":"B"}]);spool.write("right",[{"id":2,"score":9},{"id":3,"score":8}])
        node=_node("join",{"joinType":"FULL","keys":[{"left":"id","right":"id"}]});metrics=execute_node(node,ExecutionContext(spool,{"left":[("left","output")],"right":[("right","output")]},lambda:False,lambda *_:None));rows=spool.all(str(node.design_node_id))
        assert metrics["outputRows"]==3 and {row.get("id") for row in rows}=={1,2,None} and any(row.get("right_id")==3 for row in rows)


def test_quality_route_invalid_preserves_both_outputs():
    with SpoolStore(10,100) as spool:
        spool.write("source",[{"id":1},{"id":None}]);node=_node("data_quality",{"rules":[{"type":"not_null","column":"id"}],"action":"ROUTE_INVALID"});metrics=execute_node(node,ExecutionContext(spool,{"input":[("source","output")]},lambda:False,lambda *_:None))
        assert metrics["rejectedRows"]==1 and spool.all(str(node.design_node_id),"output")==[{"id":1}] and spool.all(str(node.design_node_id),"invalid")==[{"id":None}]
