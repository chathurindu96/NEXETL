"""Centralized, validated bootstrap configuration for the NEXETL backend."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

LOCAL_ENVIRONMENT_FILENAMES: tuple[str, ...] = (".env.local", ".env")
"""Untracked local secret-injection files, listed from highest precedence first."""

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
"""Repository root that owns the untracked local environment files."""


class ConfigurationError(ValueError):
    """Report invalid bootstrap configuration without including secret values."""


@dataclass(frozen=True)
class DatabaseConfiguration:
    """Validated PostgreSQL connection values owned by backend bootstrap."""

    name: str
    user: str
    password: str = field(repr=False)
    host: str = "127.0.0.1"
    port: int = 5432


@dataclass(frozen=True)
class BackendConfiguration:
    """Process-lifetime-stable settings consumed by Django bootstrap."""

    secret_key: str = field(repr=False)
    database: DatabaseConfiguration
    debug: bool
    allowed_hosts: tuple[str, ...]
    session_cookie_secure: bool
    csrf_cookie_secure: bool


# Local-development only. Owner-directed deviation from NEX-105 and
# DOC-020 §137 (no dotenv) recorded for retroactive governance; the resolved
# startup source remains the process environment as required by DES-001 §15.4.
def load_local_environment_files(directory: Path) -> tuple[Path, ...]:
    """Populate the process environment from untracked local environment files.

    Files are optional; real process-environment values always win over file values,
    and `.env.local` wins over `.env`. Returns the applied files in application order.
    """
    applied: list[Path] = []
    for filename in LOCAL_ENVIRONMENT_FILENAMES:
        path = directory / filename
        if not path.is_file():
            continue
        load_dotenv(path, override=False)
        applied.append(path)
    return tuple(applied)


def load_backend_configuration(
    environ: Mapping[str, str] | None = None,
    *,
    local_directory: Path | None = None,
) -> BackendConfiguration:
    """Resolve and validate governed backend values from the process environment.

    Supplying an explicit mapping bypasses local environment files entirely so that
    resolution stays deterministic for tests and controlled callers.
    """
    if environ is None:
        load_local_environment_files(
            REPOSITORY_ROOT if local_directory is None else local_directory
        )
        source: Mapping[str, str] = os.environ
    else:
        source = environ

    return BackendConfiguration(
        secret_key=_required_secret("NEXETL_DJANGO_SECRET_KEY", source),
        database=DatabaseConfiguration(
            name=_non_empty("NEXETL_DB_NAME", source, default="nexetl"),
            user=_non_empty("NEXETL_DB_USER", source, default="nexetl"),
            password=_required_secret("NEXETL_DB_PASSWORD", source),
            host=_non_empty("NEXETL_DB_HOST", source, default="127.0.0.1"),
            port=_port("NEXETL_DB_PORT", source, default=5432),
        ),
        debug=_strict_boolean("NEXETL_DJANGO_DEBUG", source, default=False),
        allowed_hosts=_allowed_hosts(source),
        session_cookie_secure=_strict_boolean(
            "NEXETL_SESSION_COOKIE_SECURE", source, default=True
        ),
        csrf_cookie_secure=_strict_boolean(
            "NEXETL_CSRF_COOKIE_SECURE", source, default=True
        ),
    )


def _required_secret(name: str, environ: Mapping[str, str]) -> str:
    value = environ.get(name, "").strip()
    if not value or value.lower().startswith("replace-with-"):
        raise ConfigurationError(f"{name} must be supplied with a non-placeholder value")
    return value


def _non_empty(
    name: str,
    environ: Mapping[str, str],
    *,
    default: str,
) -> str:
    value = environ.get(name, default).strip()
    if not value:
        raise ConfigurationError(f"{name} must not be empty")
    return value


def _port(name: str, environ: Mapping[str, str], *, default: int) -> int:
    raw_value = environ.get(name, str(default)).strip()
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ConfigurationError(f"{name} must be an integer from 1 through 65535") from error
    if not 1 <= value <= 65535:
        raise ConfigurationError(f"{name} must be an integer from 1 through 65535")
    return value


def _strict_boolean(
    name: str,
    environ: Mapping[str, str],
    *,
    default: bool,
) -> bool:
    raw_value = environ.get(name, str(default)).strip().lower()
    if raw_value == "true":
        return True
    if raw_value == "false":
        return False
    raise ConfigurationError(f"{name} must be exactly true or false")


def _allowed_hosts(environ: Mapping[str, str]) -> tuple[str, ...]:
    raw_value = environ.get("NEXETL_ALLOWED_HOSTS", "localhost,127.0.0.1")
    hosts = tuple(host.strip() for host in raw_value.split(",") if host.strip())
    if not hosts:
        raise ConfigurationError("NEXETL_ALLOWED_HOSTS must contain at least one host")
    return hosts
