"""Deterministic Pipeline graph compiler and immutable version publisher."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass

from django.db import transaction

from pipelines.infrastructure.persistence.models import PipelineDefinitionRecord, PipelineDesignRecord, PipelineVersionEdgeRecord, PipelineVersionNodeRecord, PipelineVersionRecord
from pipelines.node_registry import NODE_TYPE_BY_KEY
from pipelines.schema import infer_schema, schema_issues


@dataclass(frozen=True)
class CompilationResult:
    valid: bool
    issues: list[dict[str, object]]
    order: list[str]
    schemas: dict[str, list[dict[str, object]]]


def compile_snapshot(snapshot: dict[str, object]) -> CompilationResult:
    nodes_value=snapshot.get("nodes",[]); edges_value=snapshot.get("edges",[]); issues=[]
    if not isinstance(nodes_value,list) or not isinstance(edges_value,list): return CompilationResult(False,[{"code":"NEXETL_DESIGN_SHAPE_INVALID","severity":"ERROR","message":"Nodes and edges must be lists."}],[],{})
    nodes={str(item.get("id")):item for item in nodes_value if isinstance(item,dict) and item.get("id")}; adjacency={key:[] for key in nodes}; indegree={key:0 for key in nodes}; inputs={key:{} for key in nodes}; seen=set()
    for node_id,node in nodes.items():
        kind=str(node.get("kind","legacy")); definition=NODE_TYPE_BY_KEY.get(kind)
        if not definition:
            if kind != "legacy": issues.append({"code":"NEXETL_NODE_TYPE_UNKNOWN","severity":"ERROR","message":f"Node type '{kind}' is not executable.","nodeId":node_id})
            continue
        configuration=node.get("configuration",{}) if isinstance(node.get("configuration",{}),dict) else {}
        for field in definition.configuration_schema.get("required",[]):
            if field not in configuration or configuration[field] in (None,"",[]): issues.append({"code":"NEXETL_NODE_CONFIGURATION_REQUIRED","severity":"ERROR","message":f"{definition.display_name} requires '{field}'.","nodeId":node_id,"field":field})
    for edge in edges_value:
        if not isinstance(edge,dict): continue
        source,target=str(edge.get("sourceNodeId")),str(edge.get("targetNodeId")); source_port=str(edge.get("sourcePort","output")); target_port=str(edge.get("targetPort","input")); pair=(source,source_port,target,target_port)
        if source not in nodes or target not in nodes: issues.append({"code":"NEXETL_DESIGN_EDGE_NODE_MISSING","severity":"ERROR","message":"An edge references a missing node."}); continue
        if source==target or pair in seen: issues.append({"code":"NEXETL_DESIGN_EDGE_INVALID","severity":"ERROR","message":"Self or duplicate edges are not allowed."}); continue
        seen.add(pair); source_def=NODE_TYPE_BY_KEY.get(str(nodes[source].get("kind"))); target_def=NODE_TYPE_BY_KEY.get(str(nodes[target].get("kind")))
        source_ports={port.key for port in source_def.outputs} if source_def else set()
        if source_def and source_def.key=="split_router":
            routes=nodes[source].get("configuration",{}).get("routes",[]) if isinstance(nodes[source].get("configuration"),dict) else []
            source_ports.update(str(route.get("key")) for route in routes if isinstance(route,dict) and route.get("key"))
        if source_def and source_port not in source_ports: issues.append({"code":"NEXETL_PORT_INVALID","severity":"ERROR","message":f"Unknown source port '{source_port}'.","nodeId":source})
        if target_def and target_port not in {port.key for port in target_def.inputs}: issues.append({"code":"NEXETL_PORT_INVALID","severity":"ERROR","message":f"Unknown target port '{target_port}'.","nodeId":target})
        adjacency[source].append(target); indegree[target]+=1; inputs[target].setdefault(target_port,[]).append((source,source_port))
    queue=sorted(key for key,value in indegree.items() if value==0); order=[]
    while queue:
        current=queue.pop(0); order.append(current)
        for target in sorted(adjacency[current]):
            indegree[target]-=1
            if indegree[target]==0: queue.append(target); queue.sort()
    if len(order)!=len(nodes): issues.append({"code":"NEXETL_DESIGN_CYCLE","severity":"ERROR","message":"The Pipeline graph must be acyclic."})
    schemas={}
    for node_id in order:
        node=nodes[node_id]; incoming={port:[schemas.get(source,[]) for source,_ in sources] for port,sources in inputs[node_id].items()}; configuration=node.get("configuration",{}) if isinstance(node.get("configuration"),dict) else {}
        schemas[node_id]=infer_schema(str(node.get("kind")),configuration,incoming)
        for issue in schema_issues(str(node.get("kind")),configuration,incoming,schemas[node_id]): issue.setdefault("nodeId",node_id); issues.append(issue)
        definition=NODE_TYPE_BY_KEY.get(str(node.get("kind")))
        if definition:
            for port in (port for port in definition.inputs if not port.multiple):
                if not inputs[node_id].get(port.key): issues.append({"code":"NEXETL_INPUT_REQUIRED","severity":"ERROR","message":f"{definition.display_name} requires its {port.display_name} input.","nodeId":node_id,"field":port.key})
    return CompilationResult(not any(i.get("severity")=="ERROR" for i in issues),issues,order,schemas)


def design_snapshot(pipeline: PipelineDefinitionRecord) -> dict[str, object]:
    design=PipelineDesignRecord.objects.prefetch_related("nodes","edges").filter(pipeline=pipeline).first()
    if not design: return {"pipelineId":str(pipeline.id),"revision":1,"nodes":[],"edges":[]}
    nodes=[{"id":str(n.id),"kind":n.kind,"type":n.type,"label":n.label,"configurationVersion":n.configuration_version,"configuration":n.configuration,"inputSchema":n.input_schema,"outputSchema":n.output_schema,"positionX":n.position_x,"positionY":n.position_y} for n in design.nodes.all()]
    edges=[{"id":str(e.id),"sourceNodeId":str(e.source_node_id),"sourcePort":e.source_port,"targetNodeId":str(e.target_node_id),"targetPort":e.target_port} for e in design.edges.all()]
    return {"pipelineId":str(pipeline.id),"revision":design.revision,"nodes":nodes,"edges":edges}


@transaction.atomic
def publish_version(pipeline: PipelineDefinitionRecord,user) -> tuple[PipelineVersionRecord,CompilationResult]:
    pipeline=PipelineDefinitionRecord.objects.select_for_update().get(id=pipeline.id); snapshot=design_snapshot(pipeline); result=compile_snapshot(snapshot)
    legacy=[node for node in snapshot["nodes"] if node.get("kind")=="legacy"]
    if legacy:
        result=CompilationResult(False,[*result.issues,*({"code":"NEXETL_NODE_TYPE_LEGACY","severity":"ERROR","message":"Legacy nodes must be replaced with executable node types.","nodeId":node["id"]} for node in legacy)],result.order,result.schemas)
    if not result.valid: return None,result  # type: ignore[return-value]
    canonical=json.dumps(snapshot,sort_keys=True,separators=(",",":")); digest=hashlib.sha256(canonical.encode()).hexdigest(); latest=PipelineVersionRecord.objects.filter(pipeline=pipeline).order_by("-version").first()
    if latest and latest.snapshot_hash==digest: return latest,result
    version=PipelineVersionRecord.objects.create(pipeline=pipeline,version=(latest.version+1 if latest else 1),design_revision=int(snapshot["revision"]),snapshot=snapshot,snapshot_hash=digest,created_by=user if getattr(user,"is_authenticated",False) else None)
    for node in snapshot["nodes"]:
        PipelineVersionNodeRecord.objects.create(id=uuid.uuid4(),version=version,design_node_id=uuid.UUID(node["id"]),kind=node["kind"],category=node["type"],label=node["label"],configuration_version=node["configurationVersion"],configuration=node["configuration"],input_schema=node["inputSchema"],output_schema=result.schemas.get(node["id"],node["outputSchema"]),position_x=node["positionX"],position_y=node["positionY"])
    for edge in snapshot["edges"]:
        PipelineVersionEdgeRecord.objects.create(id=uuid.uuid4(),version=version,design_edge_id=uuid.UUID(edge["id"]),source_node_id=uuid.UUID(edge["sourceNodeId"]),source_port=edge["sourcePort"],target_node_id=uuid.UUID(edge["targetNodeId"]),target_port=edge["targetPort"])
    return version,result
