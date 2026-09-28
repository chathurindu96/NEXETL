# Backend Foundation Run Commands

All commands are Windows `cmd.exe` compatible. Secret examples are placeholders for local use only; choose private values and never commit them.

## Set backend process configuration

Working directory:

```text
C:\Projects\NEXETL\backend
```

Commands:

```cmd
set NEXETL_DJANGO_SECRET_KEY=YOUR_PRIVATE_LOCAL_SECRET
set NEXETL_DB_PASSWORD=YOUR_PRIVATE_LOCAL_DATABASE_PASSWORD
set NEXETL_DB_NAME=nexetl
set NEXETL_DB_USER=nexetl
set NEXETL_DB_HOST=127.0.0.1
set NEXETL_DB_PORT=5432
set NEXETL_DJANGO_DEBUG=false
set NEXETL_ALLOWED_HOSTS=localhost,127.0.0.1
set NEXETL_SESSION_COOKIE_SECURE=false
set NEXETL_CSRF_COOKIE_SECURE=false
```

Purpose:

Supplies the process-lifetime bootstrap values defined by DES-001. Local HTTP requires explicit `false` secure-cookie overrides; those values are never inferred from debug mode.

Prerequisite:

Choose private values for both required secret variables. Do not use the placeholder strings from `.env.example` unchanged.

Expected behavior:

Subsequent Django commands resolve and validate these values once when settings load.

## Synchronize the locked backend environment

Working directory: `C:\Projects\NEXETL\backend`

Command:

```cmd
uv sync --locked
```

Purpose: Reproduce the environment from `pyproject.toml` and `uv.lock`.

Prerequisite: uv and a compatible Python 3.13 runtime, or permission for uv to obtain one.

Expected behavior: uv reports the environment synchronized without rewriting lock state.

## Validate Docker Compose configuration

Working directory: `C:\Projects\NEXETL`

Command:

```cmd
docker compose config --quiet
```

Purpose: Validate the existing WP-01 PostgreSQL Compose definition.

Prerequisite: `NEXETL_DB_PASSWORD` is set in the current process.

Expected behavior: exit code 0 and no Compose validation error.

## Start PostgreSQL

Working directory: `C:\Projects\NEXETL`

Command:

```cmd
docker compose up -d postgres
```

Purpose: Start the existing loopback-bound PostgreSQL service.

Prerequisite: Docker Desktop/daemon is running and `NEXETL_DB_PASSWORD` is set.

Expected behavior: the `postgres` service becomes running without creating application-domain tables.

## Inspect PostgreSQL service state

Working directory: `C:\Projects\NEXETL`

Command:

```cmd
docker compose ps
```

Purpose: Display current Compose service state.

Prerequisite: Docker daemon is running.

Expected behavior: the PostgreSQL service is listed as running after startup.

## Run the Django system check

Working directory: `C:\Projects\NEXETL\backend`

Command:

```cmd
uv run python manage.py check
```

Purpose: Load validated settings, populate the Django/DRF bootstrap, and run framework system checks.

Prerequisite: backend process configuration is set. PostgreSQL need not be running for this configuration-only check.

Expected output:

```text
System check identified no issues (0 silenced).
```

## Verify Django database connectivity

Working directory: `C:\Projects\NEXETL\backend`

Command:

```cmd
uv run python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor)"
```

Purpose: Open and close a Django-managed PostgreSQL connection without creating schema objects.

Prerequisite: PostgreSQL is running and all backend process configuration values match the Compose service.

Expected output: `postgresql`.

## Run backend foundation tests

Working directory: `C:\Projects\NEXETL\backend`

Command:

```cmd
uv run pytest
```

Purpose: Verify deterministic configuration defaults, overrides, required secrets, strict booleans, port validation, and secret-safe representations.

Prerequisite: locked backend environment is synchronized.

Expected behavior: all backend-foundation configuration tests pass.

## Start the Django development server

Working directory: `C:\Projects\NEXETL\backend`

Command:

```cmd
uv run python manage.py runserver 127.0.0.1:8000
```

Purpose: Start the local Django development process on the DES-001 port.

Prerequisite: PostgreSQL and backend process configuration are available. No Pipeline Definition route exists in this slice.

Expected behavior: Django listens on `127.0.0.1:8000`.

## Stop the Django development server

In the terminal running Django, press:

```text
Ctrl+C
```

Purpose: Stop the foreground development process cleanly.

## Stop PostgreSQL without deleting data

Working directory: `C:\Projects\NEXETL`

Command:

```cmd
docker compose down
```

Purpose: Stop the local Compose service while preserving the named PostgreSQL volume.

Prerequisite: Docker daemon is running.

Expected behavior: the service stops; `nexetl-postgres-data` is retained. Do not add `--volumes` unless a separately authorized clean reset is intended.
