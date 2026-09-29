"""API behavior without relying on a live PostgreSQL service."""

from __future__ import annotations

from dataclasses import dataclass
from json import loads

import pytest
from django.test import Client, RequestFactory
from rest_framework.test import APIRequestFactory, force_authenticate

from nexetl.api.csrf import csrf_failure
from pipelines.api.views import PipelineDefinitionCollectionView, PipelineDefinitionDetailView, csrf_bootstrap
from pipelines.domain import PipelineDefinition, PipelineDefinitionId


@dataclass
class Principal:
    authenticated: bool = True
    permitted: bool = True

    @property
    def is_authenticated(self) -> bool:
        return self.authenticated

    def has_perm(self, _: str) -> bool:
        return self.permitted


class MemoryStore:
    definitions: dict[PipelineDefinitionId, PipelineDefinition] = {}

    def create(self, pipeline_definition: PipelineDefinition) -> None:
        self.definitions[pipeline_definition.id] = pipeline_definition

    def get(self, identifier: PipelineDefinitionId) -> PipelineDefinition | None:
        return self.definitions.get(identifier)

    def list(self, **_: object) -> tuple[list[PipelineDefinition], int]:
        values = list(self.definitions.values())
        return values, len(values)

    def update(self, pipeline_definition: PipelineDefinition) -> PipelineDefinition:
        self.definitions[pipeline_definition.id] = pipeline_definition
        return pipeline_definition


@pytest.fixture(autouse=True)
def memory_store(monkeypatch: pytest.MonkeyPatch) -> None:
    MemoryStore.definitions = {}
    monkeypatch.setattr("pipelines.api.views.DjangoPipelineDefinitionStore", MemoryStore)


def test_csrf_bootstrap_returns_success_and_sets_cookie() -> None:
    response = Client().get("/api/security/csrf/")
    assert response.status_code == 200
    assert "csrftoken" in response.cookies


def test_unauthenticated_post_is_a_governed_401() -> None:
    request = APIRequestFactory().post("/api/pipeline-definitions/", {"name": "Customer Load", "description": "Test"}, format="json")
    force_authenticate(request, user=Principal(authenticated=False))
    response = PipelineDefinitionCollectionView.as_view()(request)
    assert response.status_code == 401
    assert response.data["code"] == "NEXETL_AUTHENTICATION_REQUIRED"


def test_unsupported_method_uses_the_governed_405_contract() -> None:
    request = APIRequestFactory().put("/api/pipeline-definitions/")
    response = PipelineDefinitionCollectionView.as_view()(request)
    assert response.status_code == 405
    assert response.data["code"] == "NEXETL_METHOD_NOT_ALLOWED"


def test_unauthorized_post_is_a_governed_403() -> None:
    request = APIRequestFactory().post("/api/pipeline-definitions/")
    force_authenticate(request, user=Principal(permitted=False))
    response = PipelineDefinitionCollectionView.as_view()(request)
    assert response.status_code == 403
    assert response.data["code"] == "NEXETL_AUTHORIZATION_DENIED"


def test_authorized_post_registers_identity_and_returns_location() -> None:
    request = APIRequestFactory().post("/api/pipeline-definitions/", {"name": "Customer Load", "description": "Test"}, format="json")
    force_authenticate(request, user=Principal())
    response = PipelineDefinitionCollectionView.as_view()(request)
    assert response.status_code == 201
    assert PipelineDefinitionId.parse(response.data["id"])
    assert response["Location"] == f"/api/pipeline-definitions/{response.data['id']}/"


def test_inspection_checks_authorization_before_lookup() -> None:
    request = APIRequestFactory().get("/api/pipeline-definitions/not-a-uuid/")
    force_authenticate(request, user=Principal(permitted=False))
    response = PipelineDefinitionDetailView.as_view()(request, pipeline_definition_id="not-a-uuid")
    assert response.status_code == 403
    assert response.data["code"] == "NEXETL_AUTHORIZATION_DENIED"


def test_invalid_identifier_and_missing_definition_are_governed() -> None:
    malformed = APIRequestFactory().get("/api/pipeline-definitions/not-a-uuid/")
    force_authenticate(malformed, user=Principal())
    malformed_response = PipelineDefinitionDetailView.as_view()(malformed, pipeline_definition_id="not-a-uuid")
    assert malformed_response.status_code == 400
    assert malformed_response.data["code"] == "NEXETL_VALIDATION_FAILED"

    missing_id = str(PipelineDefinitionId.generate())
    missing = APIRequestFactory().get(f"/api/pipeline-definitions/{missing_id}/")
    force_authenticate(missing, user=Principal())
    missing_response = PipelineDefinitionDetailView.as_view()(missing, pipeline_definition_id=missing_id)
    assert missing_response.status_code == 404
    assert missing_response.data["code"] == "NEXETL_PIPELINE_DEFINITION_NOT_FOUND"


def test_csrf_failure_is_safe_and_stable() -> None:
    response = csrf_failure(RequestFactory().post("/api/pipeline-definitions/"), "sensitive reason")
    assert response.status_code == 403
    assert loads(response.content)["code"] == "NEXETL_CSRF_REJECTED"
    assert "sensitive reason" not in response.content.decode()
