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
    """The settings, root URLs, ASGI, and WSGI adapters load without feature code."""
    urls = importlib.import_module("nexetl.urls")
    asgi = importlib.import_module("nexetl.asgi")
    wsgi = importlib.import_module("nexetl.wsgi")

    assert urls.urlpatterns == []
    assert asgi.application is not None
    assert wsgi.application is not None
