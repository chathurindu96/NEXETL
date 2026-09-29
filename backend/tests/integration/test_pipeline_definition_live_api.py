"""PostgreSQL-backed integration coverage of the Increment 1 REST contract."""

from __future__ import annotations

from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient

from pipelines.infrastructure.persistence.models import PipelineDefinitionRecord


def _authenticated_client(*permissions: str) -> APIClient:
    user = get_user_model().objects.create_user(
        username=f"increment-one-{uuid4()}", password="test-only-integration-password"
    )
    if permissions:
        user.user_permissions.add(*Permission.objects.filter(codename__in=permissions))
    client = APIClient(enforce_csrf_checks=True)
    assert client.login(username=user.username, password="test-only-integration-password")
    return client


def _csrf(client: APIClient) -> str:
    response = client.get("/api/security/csrf/")
    assert response.status_code == 200
    return client.cookies["csrftoken"].value


@pytest.mark.django_db
def test_authorized_registration_persists_and_can_be_inspected() -> None:
    client = _authenticated_client("register_pipeline_definition", "inspect_pipeline_definition")

    created = client.post(
        "/api/pipeline-definitions/",
        data={"name": "Customer Load", "description": "Integration test"},
        HTTP_X_CSRFTOKEN=_csrf(client),
    )

    assert created.status_code == 201
    identifier = created.json()["id"]
    assert created["Location"] == f"/api/pipeline-definitions/{identifier}/"
    assert PipelineDefinitionRecord.objects.filter(id=identifier).exists()

    inspected = client.get(f"/api/pipeline-definitions/{identifier}/")
    assert inspected.status_code == 200
    assert inspected.json()["id"] == identifier
    assert inspected.json()["name"] == "Customer Load"


@pytest.mark.django_db
def test_live_api_security_and_error_contract() -> None:
    unauthenticated = APIClient(enforce_csrf_checks=True)
    assert unauthenticated.post("/api/pipeline-definitions/").json()["code"] == (
        "NEXETL_AUTHENTICATION_REQUIRED"
    )

    unauthorized = _authenticated_client()
    forbidden = unauthorized.get(f"/api/pipeline-definitions/{uuid4()}/")
    assert forbidden.status_code == 403
    assert forbidden.json()["code"] == "NEXETL_AUTHORIZATION_DENIED"

    authorized = _authenticated_client("inspect_pipeline_definition")
    missing = authorized.get(f"/api/pipeline-definitions/{uuid4()}/")
    assert missing.status_code == 404
    assert missing.json()["code"] == "NEXETL_PIPELINE_DEFINITION_NOT_FOUND"

    malformed = authorized.get("/api/pipeline-definitions/not-a-uuid/")
    assert malformed.status_code == 400
    assert malformed.json()["code"] == "NEXETL_VALIDATION_FAILED"

    csrf_client = _authenticated_client("register_pipeline_definition")
    csrf_rejected = csrf_client.post("/api/pipeline-definitions/")
    assert csrf_rejected.status_code == 403
    assert csrf_rejected.json()["code"] == "NEXETL_CSRF_REJECTED"

    method = authorized.post(
        f"/api/pipeline-definitions/{uuid4()}/", HTTP_X_CSRFTOKEN=_csrf(authorized)
    )
    assert method.status_code == 405
    assert method.json()["code"] == "NEXETL_METHOD_NOT_ALLOWED"


@pytest.mark.django_db
def test_registry_lifecycle_querying_and_archived_enforcement() -> None:
    client = _authenticated_client(
        "register_pipeline_definition",
        "inspect_pipeline_definition",
        "list_pipeline_definition",
        "update_pipeline_definition",
        "archive_pipeline_definition",
    )
    csrf = _csrf(client)
    first = client.post(
        "/api/pipeline-definitions/",
        data={"name": "Alpha", "description": "First"},
        HTTP_X_CSRFTOKEN=csrf,
    )
    second = client.post(
        "/api/pipeline-definitions/",
        data={"name": "Bravo", "description": "Second"},
        HTTP_X_CSRFTOKEN=csrf,
    )
    assert first.status_code == second.status_code == 201

    listed = client.get("/api/pipeline-definitions/?search=br&page=1&pageSize=1&sort=name")
    assert listed.status_code == 200
    assert listed.json()["totalItems"] == 1
    assert listed.json()["items"][0]["name"] == "Bravo"

    identifier = first.json()["id"]
    updated = client.patch(
        f"/api/pipeline-definitions/{identifier}/",
        data={"name": "Alpha Updated"},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=_csrf(client),
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Alpha Updated"

    archived = client.post(
        f"/api/pipeline-definitions/{identifier}/archive/",
        HTTP_X_CSRFTOKEN=_csrf(client),
    )
    assert archived.status_code == 200
    assert archived.json()["state"] == "ARCHIVED"
    rejected = client.patch(
        f"/api/pipeline-definitions/{identifier}/",
        data={"name": "Must not update"},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=_csrf(client),
    )
    assert rejected.status_code == 409
    assert rejected.json()["code"] == "NEXETL_PIPELINE_ARCHIVED"


@pytest.mark.django_db
def test_connector_catalogue_is_read_only_and_complete() -> None:
    client = _authenticated_client("inspect_pipeline_definition")
    response = client.get("/api/connectors/")
    assert response.status_code == 200
    assert [item["key"] for item in response.json()["items"]] == [
        "postgresql",
        "sqlserver",
        "mysql",
        "mariadb",
    ]
    detail = client.get("/api/connectors/postgresql/")
    assert detail.status_code == 200
    assert detail.json()["capabilities"] == ["read", "write"]
    assert client.post("/api/connectors/", HTTP_X_CSRFTOKEN=_csrf(client)).status_code == 405
