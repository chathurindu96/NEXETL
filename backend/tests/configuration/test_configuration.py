"""Focused verification of NEX-105 configuration resolution."""

import os
from pathlib import Path

import pytest

from nexetl.configuration import load_backend_configuration


BACKEND_ROOT = Path(__file__).resolve().parents[2]


def test_safe_defaults_are_resolved_without_secret_fallbacks() -> None:
    configuration = load_backend_configuration({})

    assert configuration.secret_key is None
    assert configuration.database.password is None
    assert configuration.database.name == "nexetl"
    assert configuration.database.user == "nexetl"
    assert configuration.database.host == "127.0.0.1"
    assert configuration.database.port == 5432
    assert configuration.debug is False
    assert configuration.allowed_hosts == ("localhost", "127.0.0.1")
    assert configuration.session_cookie_secure is True
    assert configuration.csrf_cookie_secure is True


def test_explicit_process_environment_values_are_typed() -> None:
    configuration = load_backend_configuration(
        {
            "NEXETL_DJANGO_SECRET_KEY": "test-only-secret-key",
            "NEXETL_DB_NAME": "nexetl_test",
            "NEXETL_DB_USER": "nexetl_test_user",
            "NEXETL_DB_PASSWORD": "test-only-database-password",
            "NEXETL_DB_HOST": "postgres.example.test",
            "NEXETL_DB_PORT": "5544",
            "NEXETL_DJANGO_DEBUG": "true",
            "NEXETL_ALLOWED_HOSTS": "testserver, localhost",
            "NEXETL_SESSION_COOKIE_SECURE": "false",
            "NEXETL_CSRF_COOKIE_SECURE": "false",
        }
    )

    assert configuration.secret_key == "test-only-secret-key"
    assert configuration.database.password == "test-only-database-password"
    assert configuration.database.port == 5544
    assert configuration.debug is True
    assert configuration.allowed_hosts == ("testserver", "localhost")
    assert configuration.session_cookie_secure is False
    assert configuration.csrf_cookie_secure is False


def test_secure_cookie_defaults_do_not_depend_on_debug() -> None:
    configuration = load_backend_configuration({"NEXETL_DJANGO_DEBUG": "true"})

    assert configuration.debug is True
    assert configuration.session_cookie_secure is True
    assert configuration.csrf_cookie_secure is True


def test_missing_or_placeholder_secrets_are_resolved_for_later_validation() -> None:
    configuration = load_backend_configuration(
        {
            "NEXETL_DJANGO_SECRET_KEY": "replace-with-a-real-secret",
            "NEXETL_DB_PASSWORD": "",
        }
    )

    assert configuration.secret_key == "replace-with-a-real-secret"
    assert configuration.database.password == ""


def test_configuration_representations_do_not_expose_secrets() -> None:
    configuration = load_backend_configuration(
        {
            "NEXETL_DJANGO_SECRET_KEY": "test-only-secret-key",
            "NEXETL_DB_PASSWORD": "test-only-database-password",
        }
    )

    representation = repr(configuration)

    assert "test-only-secret-key" not in representation
    assert "test-only-database-password" not in representation


def test_loader_uses_the_process_environment_when_no_mapping_is_supplied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(os, "environ", {"NEXETL_DB_PORT": "5533"})

    configuration = load_backend_configuration()

    assert configuration.database.port == 5533


def test_no_dotenv_dependency_or_local_file_loader_is_present() -> None:
    configuration_source = (
        BACKEND_ROOT / "src" / "nexetl" / "configuration.py"
    ).read_text(encoding="utf-8")
    manifest = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "dotenv" not in configuration_source.lower()
    assert "dotenv" not in manifest.lower()
    assert "load_local_environment_files" not in configuration_source


def test_raw_process_environment_access_is_centralized() -> None:
    source_root = BACKEND_ROOT / "src"
    files_with_environment_access = {
        source_file.relative_to(source_root).as_posix()
        for source_file in source_root.rglob("*.py")
        if "os.environ" in source_file.read_text(encoding="utf-8")
        or "os.getenv" in source_file.read_text(encoding="utf-8")
    }

    assert files_with_environment_access == {"nexetl/configuration.py"}
