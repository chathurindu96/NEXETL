"""Smoke tests for the narrow Django composition bootstrap."""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture
def controlled_bootstrap_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide the minimal valid process configuration needed by Django settings."""
    monkeypatch.setenv("NEXETL_DJANGO_SECRET_KEY", "test-only-bootstrap-secret")
    monkeypatch.setenv("NEXETL_DB_PASSWORD", "test-only-bootstrap-password")
    monkeypatch.setenv("NEXETL_SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("NEXETL_CSRF_COOKIE_SECURE", "false")


def test_django_bootstrap_entry_points_import(
    controlled_bootstrap_environment: None,
) -> None:
    """The settings, root URLs, ASGI, and WSGI adapters load with platform routes."""
    urls = importlib.import_module("nexetl.urls")
    asgi = importlib.import_module("nexetl.asgi")
    wsgi = importlib.import_module("nexetl.wsgi")

    assert len(urls.urlpatterns) == 5
    assert urls.urlpatterns[0].name == "service-index"
    assert urls.urlpatterns[1].name == "auth-session"
    assert urls.urlpatterns[2].name == "auth-login"
    assert urls.urlpatterns[3].name == "auth-logout"
    api_names = {pattern.name for pattern in urls.urlpatterns[4].url_patterns}
    assert {"connection-collection", "node-type-collection", "pipeline-run-collection", "pipeline-schedule-collection"} <= api_names
    assert asgi.application is not None
    assert wsgi.application is not None
