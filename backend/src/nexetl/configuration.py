"""Centralized process-environment configuration for the NEXETL backend."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field


class ConfigurationError(ValueError):
    """Report invalid backend startup configuration without exposing secrets."""


KNOWN_SECRET_PLACEHOLDERS = frozenset(
    {
        "replace-with-a-local-secret",
        "replace-with-a-local-password",
        "replace-with-a-real-secret",
        "replace-with-a-real-password",
        "your_private_local_secret",
        "your_private_local_database_password",
    }
)
"""Known documentation placeholders that are never valid runtime secrets."""


@dataclass(frozen=True)
class DatabaseConfiguration:
    """Typed PostgreSQL connection values resolved during backend bootstrap."""

    name: str
    user: str
    password: str | None = field(repr=False)
    host: str = "127.0.0.1"
    port: int = 5432


@dataclass(frozen=True)
class BackendConfiguration:
    """Typed backend values resolved exclusively from the process environment."""

    secret_key: str | None = field(repr=False)
    database: DatabaseConfiguration
    debug: bool
    allowed_hosts: tuple[str, ...]
    session_cookie_secure: bool
    csrf_cookie_secure: bool


def configure_django_settings_module() -> None:
    """Select NEXETL's Django settings module for standard Django entry points."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexetl.settings")


def load_backend_configuration(
    environ: Mapping[str, str] | None = None,
) -> BackendConfiguration:
    """Resolve typed backend settings from the process environment."""
    source: Mapping[str, str] = os.environ if environ is None else environ

    return BackendConfiguration(
        secret_key=_optional_text("NEXETL_DJANGO_SECRET_KEY", source),
        database=DatabaseConfiguration(
            name=_text("NEXETL_DB_NAME", source, default="nexetl"),
            user=_text("NEXETL_DB_USER", source, default="nexetl"),
            password=_optional_text("NEXETL_DB_PASSWORD", source),
            host=_text("NEXETL_DB_HOST", source, default="127.0.0.1"),
            port=_integer("NEXETL_DB_PORT", source, default=5432),
        ),
        debug=_boolean("NEXETL_DJANGO_DEBUG", source, default=False),
        allowed_hosts=_allowed_hosts(source),
        session_cookie_secure=_boolean(
            "NEXETL_SESSION_COOKIE_SECURE", source, default=True
        ),
        csrf_cookie_secure=_boolean(
            "NEXETL_CSRF_COOKIE_SECURE", source, default=True
        ),
    )


def validate_backend_configuration(
    configuration: BackendConfiguration,
) -> BackendConfiguration:
    """Validate resolved backend configuration before Django becomes ready."""
    _required_secret("NEXETL_DJANGO_SECRET_KEY", configuration.secret_key)
    _non_empty("NEXETL_DB_NAME", configuration.database.name)
    _non_empty("NEXETL_DB_USER", configuration.database.user)
    _required_secret("NEXETL_DB_PASSWORD", configuration.database.password)
    _non_empty("NEXETL_DB_HOST", configuration.database.host)
    _port_in_range(configuration.database.port)
    _non_empty_allowed_hosts(configuration.allowed_hosts)

    return configuration


def _optional_text(name: str, environ: Mapping[str, str]) -> str | None:
    value = environ.get(name)
    return value.strip() if value is not None else None


def _text(name: str, environ: Mapping[str, str], *, default: str) -> str:
    return environ.get(name, default).strip()


def _integer(name: str, environ: Mapping[str, str], *, default: int) -> int:
    try:
        return int(environ.get(name, str(default)).strip())
    except ValueError as error:
        raise ConfigurationError(
            f"{name} must be an integer from 1 through 65535"
        ) from error


def _boolean(name: str, environ: Mapping[str, str], *, default: bool) -> bool:
    raw_value = environ.get(name, str(default)).strip().lower()
    if raw_value == "true":
        return True
    if raw_value == "false":
        return False
    raise ConfigurationError(f"{name} must be represented as true or false")


def _allowed_hosts(environ: Mapping[str, str]) -> tuple[str, ...]:
    raw_value = environ.get("NEXETL_ALLOWED_HOSTS", "localhost,127.0.0.1")
    return tuple(host.strip() for host in raw_value.split(",") if host.strip())


def _required_secret(name: str, value: str | None) -> None:
    if value is None or not value.strip() or value.lower() in KNOWN_SECRET_PLACEHOLDERS:
        raise ConfigurationError(f"{name} must be supplied with a non-placeholder value")


def _non_empty(name: str, value: str) -> None:
    if not value.strip():
        raise ConfigurationError(f"{name} must not be empty")


def _port_in_range(value: int) -> None:
    if not 1 <= value <= 65535:
        raise ConfigurationError("NEXETL_DB_PORT must be an integer from 1 through 65535")


def _non_empty_allowed_hosts(hosts: tuple[str, ...]) -> None:
    if not hosts:
        raise ConfigurationError("NEXETL_ALLOWED_HOSTS must contain at least one host")
