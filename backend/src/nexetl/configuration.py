"""Centralized process-environment configuration for the NEXETL backend."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


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
        "replace-with-private-connection-secret-key-material",
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
class DevelopmentSuperadminConfiguration:
    """Explicitly opt-in local-only account bootstrap settings."""

    enabled: bool = False
    username: str = "admin"
    password: str = field(default="123", repr=False)


@dataclass(frozen=True)
class RuntimeConfiguration:
    batch_size: int = 1000
    preview_default_rows: int = 50
    preview_max_rows: int = 200
    preview_max_bytes: int = 1_000_000
    operation_timeout_seconds: int = 30
    worker_concurrency: int = 1
    worker_poll_seconds: int = 2
    worker_lease_seconds: int = 300
    stateful_max_rows: int = 250_000


@dataclass(frozen=True)
class BackendConfiguration:
    """Typed backend values resolved exclusively from the process environment."""

    secret_key: str | None = field(repr=False)
    database: DatabaseConfiguration
    debug: bool
    allowed_hosts: tuple[str, ...]
    session_cookie_secure: bool
    csrf_cookie_secure: bool
    csrf_trusted_origins: tuple[str, ...]
    development_superadmin: DevelopmentSuperadminConfiguration
    connection_secret_key: str | None = field(repr=False)
    runtime: RuntimeConfiguration


def configure_django_settings_module() -> None:
    """Select NEXETL's Django settings module for standard Django entry points."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexetl.settings")


def load_local_development_environment(dotenv_path: Path | None = None) -> None:
    """Load the ignored root `.env` file without overriding process authority."""
    load_dotenv(dotenv_path=dotenv_path or REPOSITORY_ROOT / ".env", override=False)


def load_backend_configuration(
    environ: Mapping[str, str] | None = None,
) -> BackendConfiguration:
    """Resolve typed settings after optional root `.env` loading for local development."""
    if environ is None:
        load_local_development_environment()
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
        csrf_trusted_origins=_trusted_origins(source),
        development_superadmin=DevelopmentSuperadminConfiguration(
            enabled=_boolean("NEXETL_DEV_SUPERADMIN_ENABLED", source, default=False),
            username=_text("NEXETL_DEV_SUPERADMIN_USERNAME", source, default="admin"),
            password=_text("NEXETL_DEV_SUPERADMIN_PASSWORD", source, default="123"),
        ),
        connection_secret_key=_optional_text("NEXETL_CONNECTION_SECRET_KEY", source),
        runtime=RuntimeConfiguration(
            batch_size=_integer("NEXETL_BATCH_SIZE", source, default=1000),
            preview_default_rows=_integer("NEXETL_PREVIEW_DEFAULT_ROWS", source, default=50),
            preview_max_rows=_integer("NEXETL_PREVIEW_MAX_ROWS", source, default=200),
            preview_max_bytes=_integer("NEXETL_PREVIEW_MAX_BYTES", source, default=1_000_000),
            operation_timeout_seconds=_integer("NEXETL_OPERATION_TIMEOUT_SECONDS", source, default=30),
            worker_concurrency=_integer("NEXETL_WORKER_CONCURRENCY", source, default=1),
            worker_poll_seconds=_integer("NEXETL_WORKER_POLL_SECONDS", source, default=2),
            worker_lease_seconds=_integer("NEXETL_WORKER_LEASE_SECONDS", source, default=300),
            stateful_max_rows=_integer("NEXETL_STATEFUL_MAX_ROWS", source, default=250_000),
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
    if configuration.connection_secret_key in KNOWN_SECRET_PLACEHOLDERS:
        raise ConfigurationError("NEXETL_CONNECTION_SECRET_KEY must not use a documentation placeholder")
    _non_empty("NEXETL_DB_HOST", configuration.database.host)
    _port_in_range(configuration.database.port)
    _non_empty_allowed_hosts(configuration.allowed_hosts)
    _valid_trusted_origins(configuration.csrf_trusted_origins)
    _range("NEXETL_BATCH_SIZE", configuration.runtime.batch_size, 1, 100_000)
    _range("NEXETL_PREVIEW_DEFAULT_ROWS", configuration.runtime.preview_default_rows, 1, configuration.runtime.preview_max_rows)
    _range("NEXETL_PREVIEW_MAX_ROWS", configuration.runtime.preview_max_rows, 1, 1000)
    _range("NEXETL_PREVIEW_MAX_BYTES", configuration.runtime.preview_max_bytes, 1024, 10_000_000)
    _range("NEXETL_OPERATION_TIMEOUT_SECONDS", configuration.runtime.operation_timeout_seconds, 1, 3600)
    _range("NEXETL_WORKER_CONCURRENCY", configuration.runtime.worker_concurrency, 1, 8)
    _range("NEXETL_WORKER_POLL_SECONDS", configuration.runtime.worker_poll_seconds, 1, 60)
    _range("NEXETL_WORKER_LEASE_SECONDS", configuration.runtime.worker_lease_seconds, 30, 3600)
    _range("NEXETL_STATEFUL_MAX_ROWS", configuration.runtime.stateful_max_rows, 1, 10_000_000)

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


def _trusted_origins(environ: Mapping[str, str]) -> tuple[str, ...]:
    raw_value = environ.get("NEXETL_CSRF_TRUSTED_ORIGINS", "")
    return tuple(origin.strip() for origin in raw_value.split(",") if origin.strip())


def _required_secret(name: str, value: str | None) -> None:
    if value is None or not value.strip() or value.lower() in KNOWN_SECRET_PLACEHOLDERS:
        raise ConfigurationError(f"{name} must be supplied with a non-placeholder value")


def _non_empty(name: str, value: str) -> None:
    if not value.strip():
        raise ConfigurationError(f"{name} must not be empty")


def _port_in_range(value: int) -> None:
    if not 1 <= value <= 65535:
        raise ConfigurationError("NEXETL_DB_PORT must be an integer from 1 through 65535")


def _range(name: str, value: int, minimum: int, maximum: int) -> None:
    if not minimum <= value <= maximum:
        raise ConfigurationError(f"{name} must be an integer from {minimum} through {maximum}")


def _non_empty_allowed_hosts(hosts: tuple[str, ...]) -> None:
    if not hosts:
        raise ConfigurationError("NEXETL_ALLOWED_HOSTS must contain at least one host")


def _valid_trusted_origins(origins: tuple[str, ...]) -> None:
    for origin in origins:
        parsed = urlparse(origin)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path not in {"", "/"}:
            raise ConfigurationError(
                "NEXETL_CSRF_TRUSTED_ORIGINS must contain comma-separated http(s) origins"
            )
