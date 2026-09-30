"""URL composition for Pipeline Definition registry and connector catalogue APIs."""

from django.urls import URLPattern, URLResolver, path

from .views import (
    ConnectorCollectionView,
    ConnectorDetailView,
    PipelineDefinitionArchiveView,
    PipelineDefinitionCollectionView,
    PipelineDefinitionDetailView,
    PipelineDesignView,
    PipelineDesignValidationView,
    csrf_bootstrap,
)
from .connections import ConnectionCollectionView, ConnectionDatasetSchemaView, ConnectionDatasetsView, ConnectionDetailView, ConnectionPreviewView, ConnectionSchemasView, ConnectionTestView
from .registry import NodeTypeCollectionView
from .runtime import OperationsSummaryView, PipelineRunCancelView, PipelineRunCollectionView, PipelineRunDetailView, PipelineRunRetryView, PipelineScheduleCollectionView, PipelineScheduleDetailView, PipelineVersionCollectionView, PipelineVersionDetailView


urlpatterns: list[URLPattern | URLResolver] = [
    path("node-types/", NodeTypeCollectionView.as_view(), name="node-type-collection"),
    path("connections/", ConnectionCollectionView.as_view(), name="connection-collection"),
    path("connections/<str:connection_id>/", ConnectionDetailView.as_view(), name="connection-detail"),
    path("connections/<str:connection_id>/test/", ConnectionTestView.as_view(), name="connection-test"),
    path("connections/<str:connection_id>/schemas/", ConnectionSchemasView.as_view(), name="connection-schemas"),
    path("connections/<str:connection_id>/datasets/", ConnectionDatasetsView.as_view(), name="connection-datasets"),
    path("connections/<str:connection_id>/datasets/<str:dataset>/schema/", ConnectionDatasetSchemaView.as_view(), name="connection-dataset-schema"),
    path("connections/<str:connection_id>/preview/", ConnectionPreviewView.as_view(), name="connection-preview"),
    path("operations/summary/", OperationsSummaryView.as_view(), name="operations-summary"),
    path("connectors/", ConnectorCollectionView.as_view(), name="connector-collection"),
    path(
        "connectors/<str:connector_key>/",
        ConnectorDetailView.as_view(),
        name="connector-detail",
    ),
    path("security/csrf/", csrf_bootstrap, name="csrf-bootstrap"),
    path(
        "pipeline-definitions/",
        PipelineDefinitionCollectionView.as_view(),
        name="pipeline-definition-collection",
    ),
    path(
        "pipeline-definitions/<str:pipeline_definition_id>/",
        PipelineDefinitionDetailView.as_view(),
        name="pipeline-definition-detail",
    ),
    path(
        "pipeline-definitions/<str:pipeline_definition_id>/archive/",
        PipelineDefinitionArchiveView.as_view(),
        name="pipeline-definition-archive",
    ),
    path("pipeline-definitions/<str:pipeline_definition_id>/design/", PipelineDesignView.as_view(), name="pipeline-design"),
    path("pipeline-definitions/<str:pipeline_definition_id>/design/validate/", PipelineDesignValidationView.as_view(), name="pipeline-design-validate"),
    path("pipeline-definitions/<str:pipeline_definition_id>/versions/", PipelineVersionCollectionView.as_view(), name="pipeline-version-collection"),
    path("pipeline-definitions/<str:pipeline_definition_id>/versions/<str:version_id>/", PipelineVersionDetailView.as_view(), name="pipeline-version-detail"),
    path("pipeline-definitions/<str:pipeline_definition_id>/runs/", PipelineRunCollectionView.as_view(), name="pipeline-run-collection"),
    path("pipeline-definitions/<str:pipeline_definition_id>/runs/<str:run_id>/", PipelineRunDetailView.as_view(), name="pipeline-run-detail"),
    path("pipeline-definitions/<str:pipeline_definition_id>/runs/<str:run_id>/cancel/", PipelineRunCancelView.as_view(), name="pipeline-run-cancel"),
    path("pipeline-definitions/<str:pipeline_definition_id>/runs/<str:run_id>/retry/", PipelineRunRetryView.as_view(), name="pipeline-run-retry"),
    path("pipeline-definitions/<str:pipeline_definition_id>/schedules/", PipelineScheduleCollectionView.as_view(), name="pipeline-schedule-collection"),
    path("pipeline-definitions/<str:pipeline_definition_id>/schedules/<str:schedule_id>/", PipelineScheduleDetailView.as_view(), name="pipeline-schedule-detail"),
]
