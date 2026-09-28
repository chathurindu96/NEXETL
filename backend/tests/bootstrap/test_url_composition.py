"""Verification of the composed Increment 1 REST routes."""

from django.urls import resolve


def test_root_composes_only_the_governed_increment_one_routes() -> None:
    assert resolve("/api/security/csrf/").url_name == "csrf-bootstrap"
    assert resolve("/api/pipeline-definitions/").func.view_class.__name__ == (
        "PipelineDefinitionCollectionView"
    )
    assert resolve(
        "/api/pipeline-definitions/00000000-0000-0000-0000-000000000000/"
    ).url_name == "pipeline-definition-detail"
