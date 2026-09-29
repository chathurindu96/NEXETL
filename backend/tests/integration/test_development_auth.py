"""Development-only Django session authentication integration tests."""

import json

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework.test import APIClient


def _csrf(client: APIClient) -> str:
    assert client.get("/api/security/csrf/").status_code == 200
    return client.cookies["csrftoken"].value


@pytest.mark.django_db
def test_development_superadmin_command_requires_both_guards(settings) -> None:  # type: ignore[no-untyped-def]
    settings.DEBUG = False
    settings.CONFIGURATION = settings.CONFIGURATION.__class__(
        **{**settings.CONFIGURATION.__dict__, "development_superadmin": settings.CONFIGURATION.development_superadmin.__class__(enabled=True)}
    )
    with pytest.raises(CommandError, match="DEBUG"):
        call_command("bootstrap_dev_superadmin")
    settings.DEBUG = True
    settings.CONFIGURATION = settings.CONFIGURATION.__class__(
        **{**settings.CONFIGURATION.__dict__, "development_superadmin": settings.CONFIGURATION.development_superadmin.__class__(enabled=False)}
    )
    with pytest.raises(CommandError, match="ENABLED"):
        call_command("bootstrap_dev_superadmin")


@pytest.mark.django_db
def test_development_superadmin_command_is_real_and_idempotent(settings) -> None:  # type: ignore[no-untyped-def]
    settings.DEBUG = True
    settings.CONFIGURATION = settings.CONFIGURATION.__class__(
        **{**settings.CONFIGURATION.__dict__, "development_superadmin": settings.CONFIGURATION.development_superadmin.__class__(enabled=True, username="admin", password="123")}
    )
    call_command("bootstrap_dev_superadmin")
    call_command("bootstrap_dev_superadmin")
    user = get_user_model().objects.get(username="admin")
    assert user.is_active and user.is_staff and user.is_superuser
    assert user.check_password("123")


@pytest.mark.django_db
def test_session_login_state_logout_and_csrf() -> None:
    get_user_model().objects.create_superuser(username="admin", password="123")
    client = APIClient(enforce_csrf_checks=True)
    assert client.get("/api/auth/session/").json() == {"authenticated": False}
    rejected = client.post("/api/auth/login/", data=json.dumps({"username": "admin", "password": "123"}), content_type="application/json")
    assert rejected.status_code == 403
    assert rejected.json()["code"] == "NEXETL_CSRF_REJECTED"
    invalid = client.post(
        "/api/auth/login/",
        data=json.dumps({"username": "admin", "password": "incorrect"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=_csrf(client),
    )
    assert invalid.status_code == 401
    assert invalid.json()["code"] == "NEXETL_AUTHENTICATION_FAILED"
    logged_in = client.post("/api/auth/login/", data=json.dumps({"username": "admin", "password": "123"}), content_type="application/json", HTTP_X_CSRFTOKEN=_csrf(client))
    assert logged_in.status_code == 204
    assert client.get("/api/auth/session/").json() == {"authenticated": True, "username": "admin"}
    protected = client.post("/api/pipeline-definitions/", HTTP_X_CSRFTOKEN=_csrf(client))
    assert protected.status_code == 201
    assert client.post("/api/auth/logout/", HTTP_X_CSRFTOKEN=_csrf(client)).status_code == 204
    assert client.get("/api/auth/session/").json() == {"authenticated": False}
    assert client.post("/api/pipeline-definitions/", HTTP_X_CSRFTOKEN=_csrf(client)).status_code == 401
