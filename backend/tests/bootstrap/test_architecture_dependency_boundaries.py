"""Repeatable AST checks for the approved Pipeline Definition layer directions."""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path

import pytest


PIPELINES_ROOT = Path(__file__).resolve().parents[2] / "src" / "pipelines"
LAYER_NAMES = ("domain", "application", "infrastructure", "api")
FORBIDDEN_IMPORT_PREFIXES = {
    "domain": (
        "django",
        "rest_framework",
        "pipelines.application",
        "pipelines.infrastructure",
        "pipelines.api",
    ),
    "application": (
        "django.db",
        "rest_framework",
        "pipelines.infrastructure",
        "pipelines.api",
    ),
    "infrastructure": ("pipelines.api",),
    "api": (),
}


def _imported_modules(source: str) -> set[str]:
    """Collect actual import targets from Python syntax, not raw text."""
    imported_modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    return imported_modules


def _violations_for_source(layer: str, source: str, module_label: str) -> list[str]:
    """Describe imports that violate the approved dependency direction."""
    violations: list[str] = []
    for imported_module in sorted(_imported_modules(source)):
        for forbidden_prefix in FORBIDDEN_IMPORT_PREFIXES[layer]:
            if imported_module == forbidden_prefix or imported_module.startswith(
                f"{forbidden_prefix}."
            ):
                violations.append(
                    f"{layer} layer: {module_label} imports forbidden dependency "
                    f"{imported_module!r}"
                )
    return violations


def _package_violations() -> list[str]:
    """Inspect every current Pipeline Definition layer module deterministically."""
    violations: list[str] = []
    for layer in LAYER_NAMES:
        for module_path in sorted((PIPELINES_ROOT / layer).rglob("*.py")):
            violations.extend(
                _violations_for_source(
                    layer,
                    module_path.read_text(encoding="utf-8"),
                    module_path.relative_to(PIPELINES_ROOT).as_posix(),
                )
            )
    return violations


def _layer_dependencies(imported_modules: Iterable[str]) -> set[str]:
    """Map absolute Pipeline imports to their target architectural layers."""
    dependencies: set[str] = set()
    for imported_module in imported_modules:
        parts = imported_module.split(".")
        if len(parts) >= 2 and parts[0] == "pipelines" and parts[1] in LAYER_NAMES:
            dependencies.add(parts[1])
    return dependencies


def _find_cycles(graph: dict[str, set[str]]) -> list[tuple[str, ...]]:
    """Return architecture-layer cycles using a small depth-first traversal."""
    cycles: list[tuple[str, ...]] = []

    def visit(node: str, path: tuple[str, ...]) -> None:
        for dependency in graph[node]:
            if dependency in path:
                cycles.append(path[path.index(dependency) :] + (dependency,))
            else:
                visit(dependency, path + (dependency,))

    for layer in graph:
        visit(layer, (layer,))
    return cycles


def test_current_pipeline_modules_follow_approved_dependency_rules() -> None:
    """Domain/core and adapters remain in the approved direction."""
    assert _package_violations() == []


def test_current_pipeline_modules_have_no_architectural_dependency_cycle() -> None:
    """Current absolute layer imports do not form a circular architectural graph."""
    graph = {
        layer: set().union(
            *(
                _layer_dependencies(
                    _imported_modules(module_path.read_text(encoding="utf-8"))
                )
                for module_path in (PIPELINES_ROOT / layer).rglob("*.py")
            )
        )
        for layer in LAYER_NAMES
    }

    assert _find_cycles(graph) == []


def test_dependency_guard_reports_a_controlled_outward_dependency() -> None:
    """Prove that an application-to-infrastructure import is reported clearly."""
    violations = _violations_for_source(
        "application",
        "from pipelines.infrastructure import persistence\n",
        "synthetic_application.py",
    )

    assert violations == [
        "application layer: synthetic_application.py imports forbidden dependency "
        "'pipelines.infrastructure'"
    ]


def test_cycle_guard_reports_a_controlled_architectural_cycle() -> None:
    """Prove that a circular layer relationship is detected deterministically."""
    assert _find_cycles({"application": {"domain"}, "domain": {"application"}}) == [
        ("application", "domain", "application"),
        ("domain", "application", "domain"),
    ]
