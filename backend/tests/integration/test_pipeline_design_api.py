"""Live API coverage for the persistent, design-time Pipeline Designer contract."""

from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient


def _client() -> APIClient:
    user = get_user_model().objects.create_user(username=f"designer-{uuid4()}", password="test-password")
    user.user_permissions.add(*Permission.objects.filter(codename__in=["register_pipeline_definition", "design_pipeline_definition"]))
    client = APIClient(enforce_csrf_checks=True)
    assert client.login(username=user.username, password="test-password")
    return client


def _csrf(client: APIClient) -> str:
    client.get("/api/security/csrf/")
    return client.cookies["csrftoken"].value


@pytest.mark.django_db
def test_design_empty_save_reload_conflict_and_validation() -> None:
    client = _client()
    pipeline = client.post("/api/pipeline-definitions/", data={"name": "Design test"}, HTTP_X_CSRFTOKEN=_csrf(client)).json()
    url = f"/api/pipeline-definitions/{pipeline['id']}/design/"
    empty = client.get(url)
    assert empty.status_code == 200 and empty.json()["revision"] == 1 and empty.json()["nodes"] == []
    source, transform, target = str(uuid4()), str(uuid4()), str(uuid4())
    payload = {"revision": 1, "nodes": [{"id": source, "type": "SOURCE", "label": "Source", "connectorKey": "postgresql", "positionX": 1, "positionY": 2}, {"id": transform, "type": "TRANSFORM", "label": "Transform", "connectorKey": None, "positionX": 3, "positionY": 4}, {"id": target, "type": "TARGET", "label": "Target", "connectorKey": "postgresql", "positionX": 5, "positionY": 6}], "edges": [{"id": str(uuid4()), "sourceNodeId": source, "targetNodeId": transform}, {"id": str(uuid4()), "sourceNodeId": transform, "targetNodeId": target}]}
    saved = client.put(url, data=payload, format="json", HTTP_X_CSRFTOKEN=_csrf(client))
    assert saved.status_code == 200 and saved.json()["revision"] == 2
    assert len(client.get(url).json()["nodes"]) == 3
    stale = client.put(url, data=payload, format="json", HTTP_X_CSRFTOKEN=_csrf(client))
    assert stale.status_code == 409 and stale.json()["code"] == "NEXETL_PIPELINE_DESIGN_REVISION_CONFLICT"
    valid = client.post(f"{url}validate/", HTTP_X_CSRFTOKEN=_csrf(client))
    assert valid.status_code == 200 and valid.json()["valid"] is True


@pytest.mark.django_db
def test_design_rejects_invalid_structure_without_replacing_saved_graph() -> None:
    client = _client()
    pipeline = client.post("/api/pipeline-definitions/", data={"name": "Invalid graph"}, HTTP_X_CSRFTOKEN=_csrf(client)).json()
    url = f"/api/pipeline-definitions/{pipeline['id']}/design/"
    invalid = {"revision": 1, "nodes": [{"id": str(uuid4()), "type": "SOURCE", "label": "Missing connector", "connectorKey": None, "positionX": 0, "positionY": 0}], "edges": []}
    response = client.put(url, data=invalid, format="json", HTTP_X_CSRFTOKEN=_csrf(client))
    assert response.status_code == 400 and response.json()["code"] == "NEXETL_PIPELINE_DESIGN_INVALID"
    assert client.get(url).json()["nodes"] == []
