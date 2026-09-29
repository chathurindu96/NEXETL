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


urlpatterns: list[URLPattern | URLResolver] = [
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
]
