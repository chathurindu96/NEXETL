"""Focused structural checks for the Pipeline Definition package boundaries."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest


PACKAGE_NAMES = (
    "pipelines.domain",
    "pipelines.application",
    "pipelines.infrastructure",
    "pipelines.api",
)
INNER_PACKAGE_NAMES = ("domain", "application")
FORBIDDEN_INNER_IMPORT_ROOTS = {"django", "rest_framework"}
PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "src" / "pipelines"


def _imported_module_roots(package_directory: Path) -> set[str]:
    """Return the top-level module names imported by package source files."""
    imported_roots: set[str] = set()
    for module_path in package_directory.rglob("*.py"):
        for node in ast.walk(ast.parse(module_path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", maxsplit=1)[0])
    return imported_roots


@pytest.fixture
def controlled_bootstrap_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide the minimal valid process configuration needed by Django settings."""
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "nexetl.settings")
    monkeypatch.setenv("NEXETL_DJANGO_SECRET_KEY", "test-only-boundary-secret")
    monkeypatch.setenv("NEXETL_DB_PASSWORD", "test-only-boundary-password")
    monkeypatch.setenv("NEXETL_SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("NEXETL_CSRF_COOKIE_SECURE", "false")


def test_pipeline_packages_import_and_django_app_registers(
    controlled_bootstrap_environment: None,
) -> None:
    """The four boundaries import and Django discovers the domain-aligned app."""
    for package_name in PACKAGE_NAMES:
        assert importlib.import_module(package_name) is not None

    from django.apps import apps
    from django import setup

    setup()
    assert apps.get_app_config("pipelines").name == "pipelines"


@pytest.mark.parametrize("package_name", INNER_PACKAGE_NAMES)
def test_inner_packages_do_not_import_framework_adapters(package_name: str) -> None:
    """Domain and application package modules stay framework-independent."""
    package_directory = PACKAGE_ROOT / package_name
    imported_roots = _imported_module_roots(package_directory)

    assert not imported_roots & FORBIDDEN_INNER_IMPORT_ROOTS
