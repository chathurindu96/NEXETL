"""DRF adapters for the governed Increment 1 Pipeline Definition API."""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from nexetl.api.authentication import NexetlSessionAuthentication
from pipelines.application import InspectPipelineDefinition, RegisterPipelineDefinition
from pipelines.domain import PipelineDefinitionId
from pipelines.infrastructure.persistence.store import DjangoPipelineDefinitionStore


@ensure_csrf_cookie
def csrf_bootstrap(_: HttpRequest) -> HttpResponse:
    """Establish Django's CSRF cookie for direct browser-to-API requests."""
    # A successful bodyless 200 keeps the existing cookie bootstrap contract while
    # allowing the browser/proxy path to retain the Set-Cookie response reliably.
    return HttpResponse(status=status.HTTP_200_OK)


class PipelineDefinitionCollectionView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def post(self, request: HttpRequest) -> Response:
        _require_capability(request, "pipelines.register_pipeline_definition")
        pipeline_definition = RegisterPipelineDefinition(DjangoPipelineDefinitionStore()).execute()
        location = reverse(
            "pipeline-definition-detail", args=[str(pipeline_definition.id)]
        )
        return Response(
            {"id": str(pipeline_definition.id)},
            status=status.HTTP_201_CREATED,
            headers={"Location": location},
        )


class PipelineDefinitionDetailView(APIView):
    authentication_classes = [NexetlSessionAuthentication]

    def get(self, request: HttpRequest, pipeline_definition_id: str) -> Response:
        _require_capability(request, "pipelines.inspect_pipeline_definition")
        try:
            identifier = PipelineDefinitionId.parse(pipeline_definition_id)
        except ValueError as error:
            raise ValidationError({"pipelineDefinitionId": "Must be a UUID."}) from error
        pipeline_definition = InspectPipelineDefinition(DjangoPipelineDefinitionStore()).execute(
            identifier
        )
        if pipeline_definition is None:
            raise NotFound("Pipeline Definition was not found.")
        return Response({"id": str(pipeline_definition.id)})


def _require_capability(request: HttpRequest, permission: str) -> None:
    if not request.user or not request.user.is_authenticated:
        raise NotAuthenticated()
    if not request.user.has_perm(permission):
        raise PermissionDenied()
