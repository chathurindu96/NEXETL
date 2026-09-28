"""URL composition for the governed Increment 1 Pipeline Definition API."""

from django.urls import URLPattern, URLResolver, path

from .views import (
    PipelineDefinitionCollectionView,
    PipelineDefinitionDetailView,
    csrf_bootstrap,
)


urlpatterns: list[URLPattern | URLResolver] = [
    path("security/csrf/", csrf_bootstrap, name="csrf-bootstrap"),
    path("pipeline-definitions/", PipelineDefinitionCollectionView.as_view()),
    path(
        "pipeline-definitions/<str:pipeline_definition_id>/",
        PipelineDefinitionDetailView.as_view(),
        name="pipeline-definition-detail",
    ),
]
