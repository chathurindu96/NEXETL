"""Centralized process-environment configuration for the NEXETL backend."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field


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
    """Resolve typed backend settings from the process environment without validation.

    This configuration boundary deliberately does not load local files or enforce
    deployment validity. NEX-106 owns fail-fast validation and semantic errors.
    """
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


def _optional_text(name: str, environ: Mapping[str, str]) -> str | None:
    value = environ.get(name)
    return value.strip() if value is not None else None


def _text(name: str, environ: Mapping[str, str], *, default: str) -> str:
    return environ.get(name, default).strip()


def _integer(name: str, environ: Mapping[str, str], *, default: int) -> int:
    return int(environ.get(name, str(default)).strip())


def _boolean(name: str, environ: Mapping[str, str], *, default: bool) -> bool:
    raw_value = environ.get(name, str(default)).strip().lower()
    if raw_value == "true":
        return True
    if raw_value == "false":
        return False
    raise ValueError(f"{name} must be represented as true or false")


def _allowed_hosts(environ: Mapping[str, str]) -> tuple[str, ...]:
    raw_value = environ.get("NEXETL_ALLOWED_HOSTS", "localhost,127.0.0.1")
    return tuple(host.strip() for host in raw_value.split(",") if host.strip())
