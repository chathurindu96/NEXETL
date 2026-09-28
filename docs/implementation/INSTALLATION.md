# Backend Foundation Installation

This document records every installation and dependency-setup command required for the first small backend-foundation slice. Run commands from Windows `cmd.exe`.

No frontend dependency is installed by this slice.

## NEX-105 configuration dependency cleanup

NEX-105 removed `python-dotenv` from `backend/pyproject.toml` and
`backend/uv.lock`. Runtime configuration is supplied only through the process
or deployment environment; `.env` files are not loaded automatically.

The removal changed no other direct dependency. Refresh the exact lock state
after a dependency change with:

```cmd
uv lock
uv sync --locked
```

## Install backend runtime dependencies

Working directory:

```text
C:\Projects\NEXETL\backend
```

Successful command used by Codex in the restricted implementation environment:

```powershell
uv --project C:\Projects\NEXETL\backend --cache-dir %LOCALAPPDATA%\Temp\nexetl-wp02-uv-cache add --python <local-Python-3.13-path> django djangorestframework 'psycopg[binary]'
```

Normal developer command:

```cmd
uv add --python 3.13 django djangorestframework "psycopg[binary]"
```

Purpose:

- Django provides the governed backend application/bootstrap framework.
- Django REST Framework establishes the governed REST adapter foundation without creating an API operation.
- Psycopg provides Django's PostgreSQL driver.
- `--python 3.13` follows the existing WP-01 backend Python boundary.

Governed basis:

- NEXETL-PLAN-001 WP-02 and WP-04 boundaries.
- NEXETL-DES-001 sections 6, 7, 15, 19 and 20.
- NEXETL-ADR-002 / Accepted.

Files affected:

- `backend/pyproject.toml`
- `backend/uv.lock`
- ignored `backend/.venv/` installation state

Manifest/lock impact:

- Changes `backend/pyproject.toml`: Yes.
- Changes `backend/uv.lock`: Yes.

Expected result:

`uv` resolves compatible versions, records direct dependencies in `pyproject.toml`, records the exact dependency graph in `uv.lock`, and synchronizes the backend virtual environment.

Resolved versions:

Recorded after installation in the **Resolved dependency versions** section below.

## Install backend test dependencies

Working directory:

```text
C:\Projects\NEXETL\backend
```

Successful command used by Codex in the restricted implementation environment:

```powershell
uv --project C:\Projects\NEXETL\backend --cache-dir %LOCALAPPDATA%\Temp\nexetl-wp02-uv-cache add --dev --python <local-Python-3.13-path> pytest pytest-django
```

Normal developer command:

```cmd
uv add --dev --python 3.13 pytest pytest-django
```

Purpose:

- pytest provides the governed backend test runner.
- pytest-django provides Django bootstrap and later database-lifecycle integration for tests.

Governed basis:

- NEXETL-DES-001 section 19.
- NEXETL-DOC-025 / Approved.
- NEXETL-ADR-002 / Accepted.

Files affected:

- `backend/pyproject.toml`
- `backend/uv.lock`
- ignored `backend/.venv/` installation state

Manifest/lock impact:

- Changes `backend/pyproject.toml`: Yes.
- Changes `backend/uv.lock`: Yes.

Expected result:

The exact test dependency graph is locked and the test runner becomes available through `uv run`.

Resolved versions:

Recorded after installation in the **Resolved dependency versions** section below.

## Reproduce the locked environment

Working directory:

```text
C:\Projects\NEXETL\backend
```

Command:

```cmd
uv sync --locked
```

Purpose:

Recreates the backend environment from committed dependency declarations and exact lock state without changing either file.

Files affected:

- ignored `backend/.venv/` installation state only

Manifest/lock impact:

- Changes `backend/pyproject.toml`: No.
- Changes `backend/uv.lock`: No.

Expected result:

`uv` reports that the resolved environment is synchronized and does not rewrite the lock file.

## Resolved dependency versions

Python used for resolution and verification: CPython 3.13.6.

Direct runtime dependencies:

- Django 6.1.1
- Django REST Framework 3.18.1
- Psycopg 3.3.6 with `psycopg-binary` 3.3.6

Direct development dependencies:

- pytest 9.1.1
- pytest-django 4.14.0

Resolved transitive dependencies:

- asgiref 3.12.1
- colorama 0.4.6
- iniconfig 2.3.0
- packaging 26.3
- pluggy 1.6.0
- Pygments 2.21.0
- sqlparse 0.6.0
- tzdata 2026.4

The authoritative exact graph is `backend/uv.lock`.
