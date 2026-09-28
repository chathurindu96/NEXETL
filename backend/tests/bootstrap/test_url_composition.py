"""Focused verification of the empty NEX-103 API composition seam."""

from __future__ import annotations

from importlib import import_module

import pytest
from django.urls import Resolver404, URLResolver, get_resolver, resolve


@pytest.fixture
def controlled_bootstrap_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide the minimal valid process configuration needed by Django settings."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "nexetl.settings")
    monkeypatch.setenv("NEXETL_DJANGO_SECRET_KEY", "test-only-url-composition-secret")
    monkeypatch.setenv("NEXETL_DB_PASSWORD", "test-only-url-composition-password")
    monkeypatch.setenv("NEXETL_SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("NEXETL_CSRF_COOKIE_SECURE", "false")


def test_root_includes_the_empty_pipeline_api_composition_seam(
    controlled_bootstrap_environment: None,
) -> None:
    """The root owns `/api/` composition while the feature API remains empty."""
    api_urls = import_module("pipelines.api.urls")
    resolver = get_resolver()

    assert api_urls.urlpatterns == []
    assert any(
        isinstance(pattern, URLResolver) and str(pattern.pattern) == "api/"
        for pattern in resolver.url_patterns
    )


@pytest.mark.parametrize(
    "route",
    [
        "/api/pipeline-definitions/",
        "/api/pipeline-definitions/00000000-0000-0000-0000-000000000000/",
        "/api/security/csrf/",
    ],
)
def test_future_business_and_csrf_routes_do_not_resolve(
    controlled_bootstrap_environment: None, route: str
) -> None:
    """NEX-103 preserves future routes without exposing their behavior early."""
    with pytest.raises(Resolver404):
        resolve(route)
