"""DRF adapters for Pipeline Definition registry and connector catalogue APIs."""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from uuid import UUID

from nexetl.api.authentication import NexetlSessionAuthentication
from pipelines.application import (
    ArchivePipelineDefinition,
    InspectPipelineDefinition,
    ListPipelineDefinitions,
    RegisterPipelineDefinition,
    UpdatePipelineDefinition,
)
from pipelines.connectors import CATALOGUE
from pipelines.domain import PipelineDefinitionId
from pipelines.infrastructure.persistence.store import DjangoPipelineDefinitionStore
from pipelines.infrastructure.persistence.models import PipelineDefinitionRecord, PipelineDesignRecord, PipelineDesignNodeRecord, PipelineDesignEdgeRecord
from pipelines.runtime.compiler import compile_snapshot


@ensure_csrf_cookie
def csrf_bootstrap(_: HttpRequest) -> HttpResponse:
    """Establish Django's CSRF cookie for direct browser-to-API requests."""
    return HttpResponse(status=status.HTTP_200_OK)


class ConnectorCollectionView(APIView):
    """Expose static, design-time connector metadata only."""

    authentication_classes = [NexetlSessionAuthentication]

    def get(self, request: HttpRequest) -> Response:
        _require_capability(request, "pipelines.inspect_pipeline_definition")
        category = request.query_params.get("category")
        if category not in {None, "SOURCE", "TARGET", "BOTH"}:
            raise ValidationError({"category": "Unsupported category."})
        connectors = [
            connector
            for connector in CATALOGUE
            if category is None or connector.category == category
        ]
        return Response({"items": [_connector_representation(connector) for connector in connectors]})


class ConnectorDetailView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def get(self, request: HttpRequest, connector_key: str) -> Response:
        _require_capability(request, "pipelines.inspect_pipeline_definition")
        for connector in CATALOGUE:
            if connector.key == connector_key:
                return Response(_connector_representation(connector))
        raise NotFound("Connector was not found.")


class PipelineDefinitionCollectionView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def get(self, request: HttpRequest) -> Response:
        _require_capability(request, "pipelines.list_pipeline_definition")
        page, page_size = _pagination(request)
        state = request.query_params.get("state")
        if state not in {None, "DRAFT", "ARCHIVED"}:
            raise ValidationError({"state": "Unsupported state."})
        sort = request.query_params.get("sort", "-updatedAt")
        if sort not in {"updatedAt", "-updatedAt", "createdAt", "-createdAt", "name", "-name"}:
            raise ValidationError({"sort": "Unsupported sort."})
        search = request.query_params.get("search", "").strip()
        definitions, total = ListPipelineDefinitions(DjangoPipelineDefinitionStore()).execute(
            page=page, page_size=page_size, search=search, state=state, sort=sort
        )
        return Response(
            {
                "items": [_representation(definition) for definition in definitions],
                "page": page,
                "pageSize": page_size,
                "totalItems": total,
                "totalPages": (total + page_size - 1) // page_size,
            }
        )

    def post(self, request: HttpRequest) -> Response:
        _require_capability(request, "pipelines.register_pipeline_definition")
        name = request.data.get("name") if isinstance(request.data, dict) else None
        description = request.data.get("description", "") if isinstance(request.data, dict) else ""
        if not isinstance(name, str) or not isinstance(description, str):
            raise ValidationError({"name": "Required string.", "description": "Must be a string."})
        try:
            pipeline_definition = RegisterPipelineDefinition(
                DjangoPipelineDefinitionStore()
            ).execute(name, description)
        except ValueError as error:
            raise ValidationError({"pipelineDefinition": str(error)}) from error
        return Response(
            _representation(pipeline_definition),
            status=status.HTTP_201_CREATED,
            headers={
                "Location": reverse(
                    "pipeline-definition-detail", args=[str(pipeline_definition.id)]
                )
            },
        )


class PipelineDefinitionDetailView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def get(self, request: HttpRequest, pipeline_definition_id: str) -> Response:
        _require_capability(request, "pipelines.inspect_pipeline_definition")
        definition = _inspect(pipeline_definition_id)
        return Response(_representation(definition))

    def patch(self, request: HttpRequest, pipeline_definition_id: str) -> Response:
        _require_capability(request, "pipelines.update_pipeline_definition")
        current = _inspect(pipeline_definition_id)
        if current.state == "ARCHIVED":
            return _archived_response()
        name = request.data.get("name", current.name)
        description = request.data.get("description", current.description)
        if not isinstance(name, str) or not isinstance(description, str):
            raise ValidationError({"pipelineDefinition": "Invalid metadata."})
        try:
            updated = UpdatePipelineDefinition(DjangoPipelineDefinitionStore()).execute(
                current.id, name, description
            )
        except ValueError as error:
            raise ValidationError({"pipelineDefinition": str(error)}) from error
        if updated is None:
            raise NotFound("Pipeline Definition was not found.")
        return Response(_representation(updated))


class PipelineDefinitionArchiveView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def post(self, request: HttpRequest, pipeline_definition_id: str) -> Response:
        _require_capability(request, "pipelines.archive_pipeline_definition")
        identifier = _identifier(pipeline_definition_id)
        archived = ArchivePipelineDefinition(DjangoPipelineDefinitionStore()).execute(identifier)
        if archived is None:
            raise NotFound("Pipeline Definition was not found.")
        return Response(_representation(archived))


class PipelineDesignView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def get(self, request: HttpRequest, pipeline_definition_id: str) -> Response:
        _require_capability(request, "pipelines.design_pipeline_definition")
        pipeline = _pipeline_record(pipeline_definition_id)
        design = PipelineDesignRecord.objects.filter(pipeline=pipeline).first()
        return Response(_design_representation(design, str(pipeline.id)))

    def put(self, request: HttpRequest, pipeline_definition_id: str) -> Response:
        _require_capability(request, "pipelines.design_pipeline_definition")
        pipeline = _pipeline_record(pipeline_definition_id)
        if pipeline.state == "ARCHIVED": return _archived_response()
        payload = request.data if isinstance(request.data, dict) else {}
        issues = _structural_issues(payload.get("nodes"), payload.get("edges"))
        if issues: return Response({"code": "NEXETL_PIPELINE_DESIGN_INVALID", "issues": issues}, status=400)
        expected = payload.get("revision")
        if not isinstance(expected, int): raise ValidationError({"revision": "Required integer."})
        with transaction.atomic():
            design, _ = PipelineDesignRecord.objects.select_for_update().get_or_create(pipeline=pipeline)
            if design.revision != expected:
                return Response({"code": "NEXETL_PIPELINE_DESIGN_REVISION_CONFLICT", "detail": "A newer Pipeline Design exists."}, status=409)
            design.nodes.all().delete()
            nodes = payload["nodes"]
            for node in nodes:
                PipelineDesignNodeRecord.objects.create(design=design, id=UUID(node["id"]), type=node["type"], kind=node.get("kind", "legacy"), label=node["label"], connector_key=node.get("connectorKey"), configuration_version=node.get("configurationVersion", 1), configuration=node.get("configuration", {}), input_schema=node.get("inputSchema", []), output_schema=node.get("outputSchema", []), position_x=node["positionX"], position_y=node["positionY"])
            for edge in payload["edges"]:
                PipelineDesignEdgeRecord.objects.create(design=design, id=UUID(edge["id"]), source_node_id=UUID(edge["sourceNodeId"]), source_port=edge.get("sourcePort", "output"), target_node_id=UUID(edge["targetNodeId"]), target_port=edge.get("targetPort", "input"))
            design.revision += 1; design.save(update_fields=["revision", "updated_at"])
        return Response(_design_representation(design, str(pipeline.id)))


class PipelineDesignValidationView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def post(self, request: HttpRequest, pipeline_definition_id: str) -> Response:
        _require_capability(request, "pipelines.design_pipeline_definition")
        pipeline = _pipeline_record(pipeline_definition_id)
        design = PipelineDesignRecord.objects.filter(pipeline=pipeline).first()
        representation = _design_representation(design, str(pipeline.id))
        result = compile_snapshot(representation)
        issues = list(result.issues)
        types = [node["type"] for node in representation["nodes"]]
        if "SOURCE" not in types: issues.append({"code": "NEXETL_DESIGN_MISSING_SOURCE", "severity": "ERROR", "message": "A complete design needs a source."})
        if "TARGET" not in types: issues.append({"code": "NEXETL_DESIGN_MISSING_TARGET", "severity": "ERROR", "message": "A complete design needs a target."})
        return Response({"valid": not any(issue.get("severity", "ERROR") == "ERROR" for issue in issues), "issues": issues, "schemas": result.schemas})


def _require_capability(request: HttpRequest, permission: str) -> None:
    if not request.user or not request.user.is_authenticated:
        raise NotAuthenticated()
    if not request.user.has_perm(permission):
        raise PermissionDenied()


def _identifier(value: str) -> PipelineDefinitionId:
    try:
        return PipelineDefinitionId.parse(value)
    except ValueError as error:
        raise ValidationError({"pipelineDefinitionId": "Must be a UUID."}) from error


def _inspect(value: str):  # type: ignore[no-untyped-def]
    definition = InspectPipelineDefinition(DjangoPipelineDefinitionStore()).execute(_identifier(value))
    if definition is None:
        raise NotFound("Pipeline Definition was not found.")
    return definition


def _pagination(request: HttpRequest) -> tuple[int, int]:
    try:
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("pageSize", 20))
    except ValueError as error:
        raise ValidationError({"pagination": "Must be integers."}) from error
    if page < 1 or not 1 <= page_size <= 100:
        raise ValidationError({"pagination": "page must be positive and pageSize must be 1 through 100."})
    return page, page_size


def _archived_response() -> Response:
    return Response(
        {"code": "NEXETL_PIPELINE_ARCHIVED", "detail": "Archived Pipeline Definitions cannot be updated."},
        status=status.HTTP_409_CONFLICT,
    )


def _representation(pipeline_definition):  # type: ignore[no-untyped-def]
    return {
        "id": str(pipeline_definition.id),
        "name": pipeline_definition.name,
        "description": pipeline_definition.description,
        "state": pipeline_definition.state,
        "createdAt": pipeline_definition.created_at.isoformat() if pipeline_definition.created_at else None,
        "updatedAt": pipeline_definition.updated_at.isoformat() if pipeline_definition.updated_at else None,
    }


def _connector_representation(connector):  # type: ignore[no-untyped-def]
    return {
        "key": connector.key,
        "displayName": connector.display_name,
        "category": connector.category,
        "description": connector.description,
        "vendor": connector.vendor,
        "version": connector.version,
        "availability": connector.availability,
        "capabilities": list(connector.capabilities),
    }


def _pipeline_record(value: str) -> PipelineDefinitionRecord:
    try:
        return PipelineDefinitionRecord.objects.get(id=_identifier(value).value)
    except PipelineDefinitionRecord.DoesNotExist as error:
        raise NotFound("Pipeline Definition was not found.") from error


def _design_representation(design: PipelineDesignRecord | None, pipeline_id: str) -> dict[str, object]:
    if design is None:
        return {"pipelineId": pipeline_id, "revision": 1, "nodes": [], "edges": [], "updatedAt": None}
    nodes = list(design.nodes.all())
    return {"pipelineId": pipeline_id, "revision": design.revision, "updatedAt": design.updated_at.isoformat(), "nodes": [{"id": str(node.id), "type": node.type, "kind": node.kind, "label": node.label, "connectorKey": node.connector_key, "configurationVersion": node.configuration_version, "configuration": node.configuration, "inputSchema": node.input_schema, "outputSchema": node.output_schema, "positionX": node.position_x, "positionY": node.position_y} for node in nodes], "edges": [{"id": str(edge.id), "sourceNodeId": str(edge.source_node_id), "sourcePort": edge.source_port, "targetNodeId": str(edge.target_node_id), "targetPort": edge.target_port} for edge in design.edges.all()]}


def _structural_issues(nodes: object, edges: object) -> list[dict[str, str]]:
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return [{"code": "NEXETL_DESIGN_SHAPE_INVALID", "message": "nodes and edges must be lists."}]
    node_map: dict[str, dict] = {}
    issues: list[dict[str, str]] = []
    for node in nodes:
        if not isinstance(node, dict) or not all(key in node for key in ("id", "type", "label", "positionX", "positionY")):
            issues.append({"code": "NEXETL_DESIGN_NODE_INVALID", "message": "A node is invalid."}); continue
        if node["type"] not in {"SOURCE", "TRANSFORM", "TARGET", "GOVERNANCE"}:
            issues.append({"code": "NEXETL_DESIGN_NODE_TYPE_INVALID", "message": "Unsupported node type."})
        connector = node.get("connectorKey")
        if node.get("kind", "legacy") == "legacy" and node["type"] in {"SOURCE", "TARGET"} and not connector: issues.append({"code": "NEXETL_DESIGN_CONNECTOR_REQUIRED", "message": "Legacy source and target nodes need a connector.", "nodeId": str(node["id"])})
        if node["type"] == "TRANSFORM" and connector: issues.append({"code": "NEXETL_DESIGN_CONNECTOR_FORBIDDEN", "message": "Transform nodes cannot have a connector.", "nodeId": str(node["id"])})
        if connector and not any(item.key == connector for item in CATALOGUE): issues.append({"code": "NEXETL_CONNECTOR_NOT_FOUND", "message": "Connector was not found.", "nodeId": str(node["id"])})
        node_map[str(node["id"])] = node
    seen: set[tuple[str, str]] = set(); incoming: set[str] = set(); outgoing: set[str] = set(); graph: dict[str, list[str]] = {}
    for edge in edges:
        if not isinstance(edge, dict): issues.append({"code": "NEXETL_DESIGN_EDGE_INVALID", "message": "An edge is invalid."}); continue
        source, target = str(edge.get("sourceNodeId")), str(edge.get("targetNodeId"))
        if source not in node_map or target not in node_map: issues.append({"code": "NEXETL_DESIGN_EDGE_NODE_MISSING", "message": "An edge references a missing node."}); continue
        if source == target: issues.append({"code": "NEXETL_DESIGN_SELF_EDGE", "message": "A node cannot connect to itself."}); continue
        if (source, target) in seen: issues.append({"code": "NEXETL_DESIGN_DUPLICATE_EDGE", "message": "Duplicate edge."}); continue
        seen.add((source,target)); incoming.add(target); outgoing.add(source); graph.setdefault(source, []).append(target)
    for key,node in node_map.items():
        if node["type"] == "SOURCE" and key in incoming: issues.append({"code": "NEXETL_DESIGN_SOURCE_INBOUND", "message": "A source cannot receive an edge.", "nodeId": key})
        if node["type"] == "TARGET" and key in outgoing: issues.append({"code": "NEXETL_DESIGN_TARGET_OUTBOUND", "message": "A target cannot emit an edge.", "nodeId": key})
    visited: set[str] = set(); stack: set[str] = set()
    def cyclic(node: str) -> bool:
        if node in stack: return True
        if node in visited: return False
        visited.add(node); stack.add(node); result = any(cyclic(next_node) for next_node in graph.get(node, [])); stack.remove(node); return result
    if any(cyclic(node) for node in node_map): issues.append({"code": "NEXETL_DESIGN_CYCLE", "message": "The design must be acyclic."})
    return issues
