"""Focused verification of NEX-105 configuration resolution."""

import os
from pathlib import Path
import json
import subprocess
import sys

import pytest

from nexetl.configuration import (
    ConfigurationError,
    load_backend_configuration,
    load_local_development_environment,
    validate_backend_configuration,
)


BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _complete_values() -> dict[str, str]:
    return {
        "NEXETL_DJANGO_SECRET_KEY": "test-only-secret-key",
        "NEXETL_DB_PASSWORD": "test-only-database-password",
    }


def _validated_configuration(values: dict[str, str]):
    return validate_backend_configuration(load_backend_configuration(values))


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
    assert configuration.csrf_trusted_origins == ()


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
            "NEXETL_CSRF_TRUSTED_ORIGINS": "http://localhost:5173, https://example.test",
        }
    )

    assert configuration.secret_key == "test-only-secret-key"
    assert configuration.database.password == "test-only-database-password"
    assert configuration.database.port == 5544
    assert configuration.debug is True
    assert configuration.allowed_hosts == ("testserver", "localhost")
    assert configuration.session_cookie_secure is False
    assert configuration.csrf_cookie_secure is False
    assert configuration.csrf_trusted_origins == ("http://localhost:5173", "https://example.test")


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

    monkeypatch.setattr(
        "nexetl.configuration.load_local_development_environment", lambda: None
    )
    configuration = load_backend_configuration()

    assert configuration.database.port == 5533


def test_dotenv_loading_is_centralized_in_the_configuration_boundary() -> None:
    configuration_source = (
        BACKEND_ROOT / "src" / "nexetl" / "configuration.py"
    ).read_text(encoding="utf-8")
    manifest = (BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "from dotenv import load_dotenv" in configuration_source
    assert "load_local_development_environment" in configuration_source
    assert 'python-dotenv' in manifest


def test_values_are_loaded_from_a_local_dotenv_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "NEXETL_DJANGO_SECRET_KEY=dotenv-test-secret\n"
        "NEXETL_DB_PASSWORD=dotenv-test-password\n"
        "NEXETL_DB_PORT=5433\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(os, "environ", {})

    load_local_development_environment(dotenv)
    configuration = load_backend_configuration()

    assert configuration.secret_key == "dotenv-test-secret"
    assert configuration.database.password == "dotenv-test-password"
    assert configuration.database.port == 5433


def test_process_environment_overrides_local_dotenv(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("NEXETL_DB_PORT=5433\n", encoding="utf-8")
    monkeypatch.setattr(os, "environ", {"NEXETL_DB_PORT": "55432"})

    load_local_development_environment(dotenv)

    assert load_backend_configuration().database.port == 55432


def test_raw_process_environment_access_is_centralized() -> None:
    source_root = BACKEND_ROOT / "src"
    files_with_environment_access = {
        source_file.relative_to(source_root).as_posix()
        for source_file in source_root.rglob("*.py")
        if "os.environ" in source_file.read_text(encoding="utf-8")
        or "os.getenv" in source_file.read_text(encoding="utf-8")
    }

    assert files_with_environment_access == {"nexetl/configuration.py"}


@pytest.mark.parametrize("name", ["NEXETL_DJANGO_SECRET_KEY", "NEXETL_DB_PASSWORD"])
@pytest.mark.parametrize("value", [None, "", "   "])
def test_required_secrets_are_rejected_without_leaking_values(
    name: str, value: str | None
) -> None:
    values = _complete_values()
    if value is None:
        del values[name]
    else:
        values[name] = value

    with pytest.raises(ConfigurationError, match=name) as error:
        _validated_configuration(values)

    assert "test-only-secret" not in str(error.value)
    assert "test-only-database-password" not in repr(error.value)


@pytest.mark.parametrize(
    ("name", "placeholder"),
    [
        ("NEXETL_DJANGO_SECRET_KEY", "replace-with-a-local-secret"),
        ("NEXETL_DB_PASSWORD", "replace-with-a-local-password"),
        ("NEXETL_DJANGO_SECRET_KEY", "YOUR_PRIVATE_LOCAL_SECRET"),
    ],
)
def test_documented_secret_placeholders_are_rejected_safely(
    name: str, placeholder: str
) -> None:
    values = _complete_values() | {name: placeholder}

    with pytest.raises(ConfigurationError, match=name) as error:
        _validated_configuration(values)

    assert placeholder not in str(error.value)
    assert placeholder not in repr(error.value)


@pytest.mark.parametrize("name", ["NEXETL_DB_NAME", "NEXETL_DB_USER", "NEXETL_DB_HOST"])
@pytest.mark.parametrize("value", ["", "   "])
def test_database_text_values_reject_explicit_empty_overrides(
    name: str, value: str
) -> None:
    with pytest.raises(ConfigurationError, match=name):
        _validated_configuration(_complete_values() | {name: value})


@pytest.mark.parametrize("value", ["not-a-port", "0", "65536"])
def test_invalid_database_port_has_a_controlled_failure(value: str) -> None:
    with pytest.raises(ConfigurationError, match="NEXETL_DB_PORT"):
        _validated_configuration(_complete_values() | {"NEXETL_DB_PORT": value})


@pytest.mark.parametrize("value", ["1", "65535"])
def test_database_port_boundary_values_are_valid(value: str) -> None:
    configuration = _validated_configuration(
        _complete_values() | {"NEXETL_DB_PORT": value}
    )

    assert configuration.database.port == int(value)


@pytest.mark.parametrize(
    "name",
    [
        "NEXETL_DJANGO_DEBUG",
        "NEXETL_SESSION_COOKIE_SECURE",
        "NEXETL_CSRF_COOKIE_SECURE",
    ],
)
@pytest.mark.parametrize("value", ["yes", "no", "1", "0", "on", "off"])
def test_invalid_boolean_has_a_controlled_failure(name: str, value: str) -> None:
    with pytest.raises(ConfigurationError, match=name):
        load_backend_configuration(_complete_values() | {name: value})


@pytest.mark.parametrize("value", ["", "   ", ",,", " , , "])
def test_allowed_hosts_must_resolve_to_a_non_empty_list(value: str) -> None:
    with pytest.raises(ConfigurationError, match="NEXETL_ALLOWED_HOSTS"):
        _validated_configuration(_complete_values() | {"NEXETL_ALLOWED_HOSTS": value})


@pytest.mark.parametrize("value", ["localhost:5173", "ftp://localhost:5173", "http://localhost:5173/path"])
def test_trusted_origins_must_be_http_origins(value: str) -> None:
    with pytest.raises(ConfigurationError, match="NEXETL_CSRF_TRUSTED_ORIGINS"):
        _validated_configuration(_complete_values() | {"NEXETL_CSRF_TRUSTED_ORIGINS": value})


def test_complete_configuration_validates_deterministically() -> None:
    configuration = _validated_configuration(
        _complete_values()
        | {
            "NEXETL_DJANGO_DEBUG": "false",
            "NEXETL_ALLOWED_HOSTS": "localhost,127.0.0.1",
            "NEXETL_SESSION_COOKIE_SECURE": "true",
            "NEXETL_CSRF_COOKIE_SECURE": "true",
        }
    )

    assert configuration.secret_key == "test-only-secret-key"
    assert configuration.database.password == "test-only-database-password"


def test_invalid_configuration_prevents_django_system_check_without_secret_leak() -> None:
    environment = os.environ.copy()
    environment.update(_complete_values())
    environment["NEXETL_DJANGO_SECRET_KEY"] = "replace-with-a-local-secret"

    result = subprocess.run(
        [sys.executable, "manage.py", "check"],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode != 0
    assert "NEXETL_DJANGO_SECRET_KEY" in output
    assert "replace-with-a-local-secret" not in output


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        (
            {},
            {
                "name": "nexetl",
                "user": "nexetl",
                "host": "127.0.0.1",
                "port": 5432,
            },
        ),
        (
            {
                "NEXETL_DB_NAME": "nexetl_mapping_test",
                "NEXETL_DB_USER": "mapping_user",
                "NEXETL_DB_HOST": "192.0.2.10",
                "NEXETL_DB_PORT": "55432",
            },
            {
                "name": "nexetl_mapping_test",
                "user": "mapping_user",
                "host": "192.0.2.10",
                "port": 55432,
            },
        ),
    ],
)
def test_django_database_settings_map_governed_postgresql_values(
    overrides: dict[str, str], expected: dict[str, str | int]
) -> None:
    environment = os.environ.copy()
    password = "test-only-database-password"
    environment.update(
        {
            "NEXETL_DJANGO_SECRET_KEY": "test-only-secret-key",
            "NEXETL_DB_PASSWORD": password,
            "NEXETL_DB_NAME": str(expected["name"]),
            "NEXETL_DB_USER": str(expected["user"]),
            "NEXETL_DB_HOST": str(expected["host"]),
            "NEXETL_DB_PORT": str(expected["port"]),
        }
        | overrides
    )
    script = """
import json
import sys
sys.path.insert(0, 'src')
import nexetl.settings as settings
database = settings.DATABASES['default']
print(json.dumps({
    'engine': database['ENGINE'],
    'name': database['NAME'],
    'user': database['USER'],
    'host': database['HOST'],
    'port': database['PORT'],
    'password_matches': database['PASSWORD'] == 'test-only-database-password',
}))
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    mapped = json.loads(result.stdout)
    assert mapped == {
        "engine": "django.db.backends.postgresql",
        **expected,
        "password_matches": True,
    }
    assert password not in result.stdout


def test_compose_keeps_governed_postgresql_bootstrap_and_port_mapping() -> None:
    compose = (BACKEND_ROOT.parent / "compose.yaml").read_text(encoding="utf-8")

    assert "POSTGRES_DB: ${NEXETL_DB_NAME:-nexetl}" in compose
    assert "POSTGRES_USER: ${NEXETL_DB_USER:-nexetl}" in compose
    assert "POSTGRES_PASSWORD: ${NEXETL_DB_PASSWORD:?NEXETL_DB_PASSWORD must be set}" in compose
    assert '"127.0.0.1:${NEXETL_DB_PORT:-5432}:5432"' in compose
