"""Focused verification of backend bootstrap configuration."""

import os
from pathlib import Path

import pytest

from nexetl.configuration import (
    ConfigurationError,
    load_backend_configuration,
    load_local_environment_files,
)


def _required_values() -> dict[str, str]:
    return {
        "NEXETL_DJANGO_SECRET_KEY": "test-only-secret-key",
        "NEXETL_DB_PASSWORD": "test-only-database-password",
    }


def test_safe_local_defaults_are_applied() -> None:
    configuration = load_backend_configuration(_required_values())

    assert configuration.debug is False
    assert configuration.allowed_hosts == ("localhost", "127.0.0.1")
    assert configuration.database.name == "nexetl"
    assert configuration.database.user == "nexetl"
    assert configuration.database.host == "127.0.0.1"
    assert configuration.database.port == 5432
    assert configuration.session_cookie_secure is True
    assert configuration.csrf_cookie_secure is True


def test_explicit_environment_values_override_safe_defaults() -> None:
    values = _required_values() | {
        "NEXETL_DB_NAME": "nexetl_test",
        "NEXETL_DB_USER": "nexetl_test_user",
        "NEXETL_DB_HOST": "postgres.example.test",
        "NEXETL_DB_PORT": "5544",
        "NEXETL_DJANGO_DEBUG": "true",
        "NEXETL_ALLOWED_HOSTS": "testserver,localhost",
        "NEXETL_SESSION_COOKIE_SECURE": "false",
        "NEXETL_CSRF_COOKIE_SECURE": "false",
    }

    configuration = load_backend_configuration(values)

    assert configuration.debug is True
    assert configuration.allowed_hosts == ("testserver", "localhost")
    assert configuration.database.name == "nexetl_test"
    assert configuration.database.user == "nexetl_test_user"
    assert configuration.database.host == "postgres.example.test"
    assert configuration.database.port == 5544
    assert configuration.session_cookie_secure is False
    assert configuration.csrf_cookie_secure is False


@pytest.mark.parametrize(
    "missing_name",
    ["NEXETL_DJANGO_SECRET_KEY", "NEXETL_DB_PASSWORD"],
)
def test_required_secrets_have_no_fallback(missing_name: str) -> None:
    values = _required_values()
    del values[missing_name]

    with pytest.raises(ConfigurationError, match=missing_name):
        load_backend_configuration(values)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("NEXETL_DJANGO_SECRET_KEY", "replace-with-a-local-secret"),
        ("NEXETL_DB_PASSWORD", "replace-with-a-local-password"),
    ],
)
def test_documented_secret_placeholders_are_rejected(name: str, value: str) -> None:
    values = _required_values() | {name: value}

    with pytest.raises(ConfigurationError, match=name):
        load_backend_configuration(values)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("NEXETL_DJANGO_DEBUG", "1"),
        ("NEXETL_SESSION_COOKIE_SECURE", "yes"),
        ("NEXETL_CSRF_COOKIE_SECURE", "off"),
    ],
)
def test_booleans_are_strict(name: str, value: str) -> None:
    values = _required_values() | {name: value}

    with pytest.raises(ConfigurationError, match=name):
        load_backend_configuration(values)


@pytest.mark.parametrize("value", ["0", "65536", "not-a-port"])
def test_database_port_must_be_in_range(value: str) -> None:
    values = _required_values() | {"NEXETL_DB_PORT": value}

    with pytest.raises(ConfigurationError, match="NEXETL_DB_PORT"):
        load_backend_configuration(values)


def test_configuration_representations_do_not_expose_secrets() -> None:
    configuration = load_backend_configuration(_required_values())

    representation = repr(configuration)

    assert "test-only-secret-key" not in representation
    assert "test-only-database-password" not in representation


def test_local_environment_files_are_optional(tmp_path: Path) -> None:
    assert load_local_environment_files(tmp_path) == ()


def test_local_environment_files_apply_in_precedence_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".env").write_text(
        "NEXETL_DJANGO_SECRET_KEY=from-dot-env\n"
        "NEXETL_DB_PASSWORD=from-dot-env\n"
        "NEXETL_DB_PORT=5439\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.local").write_text("NEXETL_DB_PORT=5533\n", encoding="utf-8")
    monkeypatch.setattr(os, "environ", {})

    applied = load_local_environment_files(tmp_path)

    assert applied == (tmp_path / ".env.local", tmp_path / ".env")
    assert os.environ["NEXETL_DJANGO_SECRET_KEY"] == "from-dot-env"
    assert os.environ["NEXETL_DB_PORT"] == "5533"


def test_process_environment_values_win_over_local_environment_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".env").write_text(
        "NEXETL_DJANGO_SECRET_KEY=from-dot-env\nNEXETL_DB_PASSWORD=from-dot-env\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        os,
        "environ",
        {
            "NEXETL_DJANGO_SECRET_KEY": "from-process-environment",
            "NEXETL_DB_PASSWORD": "from-process-environment",
        },
    )

    configuration = load_backend_configuration(local_directory=tmp_path)

    assert configuration.secret_key == "from-process-environment"
    assert os.environ["NEXETL_DB_PASSWORD"] == "from-process-environment"


def test_local_environment_file_values_are_validated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".env.local").write_text(
        "NEXETL_DJANGO_SECRET_KEY=replace-with-a-local-secret\n"
        "NEXETL_DB_PASSWORD=local-only-password\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(os, "environ", {})

    with pytest.raises(ConfigurationError, match="NEXETL_DJANGO_SECRET_KEY"):
        load_backend_configuration(local_directory=tmp_path)


def test_explicit_mapping_bypasses_local_environment_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".env").write_text(
        "NEXETL_DJANGO_SECRET_KEY=from-dot-env\n"
        "NEXETL_DB_PASSWORD=from-dot-env\n"
        "NEXETL_DB_PORT=5999\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(os, "environ", {})

    configuration = load_backend_configuration(
        _required_values(), local_directory=tmp_path
    )

    assert configuration.database.port == 5432
    assert os.environ == {}
