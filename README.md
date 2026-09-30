# NEXETL

NEXETL is a next-generation extensible ETL and data integration platform.

## Project Status

The repository contains the NEXETL modular-monolith application and its complete
Pipeline lifecycle increment: configured database Connections, schema-aware
visual authoring, immutable executable versions, a PostgreSQL-backed Run queue,
dedicated worker and scheduler processes, operational Run history, and guarded
database source/target execution.

## Technology Direction

- Backend: Python / Django / Django REST Framework
- Frontend: Svelte
- Metadata Database: PostgreSQL
- API: REST / OpenAPI 3.1
- Architecture: Modular Monolith
- Deployment Direction: Containerized
- Extensibility: Connector and extension/plugin architecture

## Documentation

Controlled project documentation is available under:

`/docs`

The authoritative controlled baseline is maintained separately in
the NEXETL Google Drive.

Local documentation in this repository is provided as development
reference material.

Changes to local documentation do not automatically constitute an
approved change to the controlled NEXETL baseline.

## Repository Layout

- `backend/` owns Python project metadata, the `uv` lockfile, and backend tests.
- `frontend/` owns npm project metadata, the npm lockfile, and frontend tests.
- `tests/e2e/` is the repository-level browser acceptance boundary; Playwright
  dependencies are owned by the frontend boundary.
- `compose.yaml` defines the local PostgreSQL dependency only.

No root workspace package manager or monorepo orchestrator is used.

## Prerequisites

- Git
- uv
- Node.js and npm
- Docker with Docker Compose

The Python interpreter is managed through `uv`; a separate system Python is
not required for the locked backend environment.

## Initial Setup

Create an untracked local environment file and replace every secret placeholder
before starting PostgreSQL:

```cmd
copy .env.example .env.local
```

Install the locked backend and frontend dependency states independently:

```cmd
cd backend
uv sync --locked
cd ..\frontend
npm ci
cd ..
```

Start only the local PostgreSQL dependency:

```cmd
docker compose --env-file .env.local up -d postgres
```

Stop it without deleting the persistent developer volume:

```cmd
docker compose --env-file .env.local down
```

To validate the Compose model without starting services:

```cmd
docker compose --env-file .env.local config --quiet
```

Do not use `down --volumes` unless an intentional local database reset is
required. Django, SvelteKit, migrations, and executable test commands are added
only by their later authorized work packages.

## Development Governance

Implementation must conform to the approved NEXETL requirements,
architecture, detailed designs, ADRs, engineering standards and
testing strategy.

Architecture changes must follow the NEXETL governance and ADR
process.
