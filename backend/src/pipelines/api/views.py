"""DRF adapters for Pipeline Definition registry and connector catalogue APIs."""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

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
