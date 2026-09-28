# Backend Foundation — First Small Slice

## Scope and result

This slice implements the minimum Django/DRF bootstrap, centralized validated settings resolution, PostgreSQL connection configuration, dependency lock state, and focused configuration verification required to begin PLAN-001 WP-02 safely.

It does not complete all of WP-02 and does not begin a later domain, persistence, security, API, or frontend slice.

NEX-101 reassessed this existing shell rather than regenerating it. Its focused
bootstrap-import verification and acceptance evidence are recorded in
`docs/implementation/sprint-001/NEX-101-EVIDENCE.md`.

NEX-102 adds the approved `pipelines` Django-app/package boundary only. Its
layer mapping and focused structural verification are recorded in
`docs/implementation/sprint-001/NEX-102-EVIDENCE.md`.

NEX-103 adds the empty `/api/` URL-composition seam only. Its resolver
inventory and negative-route verification are recorded in
`docs/implementation/sprint-001/NEX-103-EVIDENCE.md`.

## Applicable requirements

- NEXETL-REQ-095 — Secret Confidentiality
- NEXETL-REQ-112 — Explicit Responsibility Boundaries
- NEXETL-REQ-113 — Controlled Configuration
- NEXETL-REQ-114 — Governed Change Traceability
- NEXETL-REQ-115 — Independent Core Behavior Verification
- NEXETL-REQ-117 — Deterministic Testability
- NEXETL-REQ-119 — Containerized Deployment Portability
- NEXETL-REQ-120 — Environment-Specific Dependency Governance

No functional Pipeline Definition requirement is implemented by this bootstrap slice.

## Traceability

| Requirement | Design/ADR | Implementation File | Verification |
|-------------|------------|---------------------|--------------|
| REQ-095 | ADR-006; DES-001 §15.1–15.5; DOC-020 §§40–45 | `backend/src/nexetl/configuration.py`, `backend/src/nexetl/settings.py`, `.env.example` (reviewed, unchanged) | required-secret and secret-safe-representation tests; Git ignore inspection |
| REQ-112 | ADR-001; DES-001 §§6–7; DOC-016 §§11–28 | `backend/manage.py`, `backend/src/nexetl/`, `backend/pyproject.toml` | Django system check; file/boundary review |
| REQ-113 | ADR-006; DES-001 §15; DOC-020 §§10–45 | `backend/src/nexetl/configuration.py`, `backend/src/nexetl/settings.py` | defaults, override, strict boolean, port, required-value tests |
| REQ-114 | PLAN-001 WP-02; DES-001 §25 | `docs/implementation/backend-foundation.md`, `docs/implementation/COMMAND-LOG.md` | traceability and command-log review |
| REQ-115 | DES-001 §19; DOC-025 §§33–50 | `backend/tests/configuration/test_configuration.py` | 13 focused tests pass without PostgreSQL |
| REQ-117 | DES-001 §§15.5 and 19; DOC-025 §§194–200 | `backend/tests/configuration/test_configuration.py` | equivalent controlled mappings produce deterministic settings |
| REQ-119 | DES-001 §20; PLAN-001 WP-04 boundary | `backend/src/nexetl/settings.py`, existing `compose.yaml`, `docs/implementation/DATABASE.md` | Compose configuration validation passed; runtime blocked by daemon state |
| REQ-120 | ADR-002; ADR-006; DES-001 §§15 and 20 | `backend/pyproject.toml`, `backend/uv.lock`, `backend/src/nexetl/configuration.py` | `uv lock --check --offline`; locked environment sync |

Applicable Accepted ADRs are ADR-001 (Core Monorepo), ADR-002 (uv and committed lock state), ADR-004 (secure session/CSRF bootstrap constraints only), and ADR-006 (concern-specific centralized configuration resolution). ADR-003, ADR-005, and ADR-007 were reviewed as part of the baseline but introduce no implementation in this slice.

## Settings and configuration structure

- `nexetl.configuration` is the only raw backend environment-reading boundary.
- `nexetl.settings` converts validated values into Django settings.
- Required secrets have no fallback and known `.env.example` placeholders are rejected.
- Non-secret local defaults are exactly those established by DES-001.
- Explicit environment values override safe documented defaults per ADR-006.
- Secure cookie defaults are `true`; local HTTP must explicitly set both flags to `false`.
- Bootstrap configuration is process-lifetime stable; no hot reload or runtime override mechanism exists.
- No dotenv/configuration framework or secret-provider product was introduced.

## File-by-file explanation

### `backend/manage.py`

Why it exists: provides the DES-001 Django command entry point and makes the `src` package available for local commands.

What it does: selects `nexetl.settings` and delegates to Django's management-command runner.

What it does not do: it does not load `.env` files, run migrations automatically, create data, or start background work.

### `backend/src/nexetl/__init__.py`

Why it exists: establishes the governed Django bootstrap/composition Python package.

What it does: documents package responsibility.

What it does not do: it has no import-time wiring or hidden behavior.

### `backend/src/nexetl/configuration.py`

Why it exists: implements ADR-006's centralized startup-resolution boundary in a small testable module.

What it does: validates required secrets, safe defaults, explicit overrides, host lists, strict booleans, and the PostgreSQL port. Secret fields are excluded from representations.

What it does not do: it does not read files, contact a secret manager, introduce universal precedence, support hot reload, or expose values to the frontend.

### `backend/src/nexetl/settings.py`

Why it exists: supplies Django's governed bootstrap settings.

What it does: configures the minimal Django/DRF framework shell, middleware, PostgreSQL backend, and session/CSRF cookie bootstrap values from validated configuration.

What it does not do: it does not define domain models, API behavior, authentication flows, authorization policy, migrations, error catalogues, or routes.

### `backend/src/nexetl/urls.py`

Why it exists: provides the required Django root URL composition point.

What it does: exposes an intentionally empty route list.

What it does not do: it does not create Pipeline Definition or security endpoints.

### `backend/src/nexetl/asgi.py`

Why it exists: provides Django's standard ASGI bootstrap entry point.

What it does: loads the governed settings module and creates the ASGI application object.

What it does not do: it does not select an asynchronous runtime architecture or background-work mechanism.

### `backend/src/nexetl/wsgi.py`

Why it exists: provides Django's standard WSGI bootstrap entry point.

What it does: loads the governed settings module and creates the WSGI application object.

What it does not do: it does not define production hosting or deployment topology.

### `backend/pyproject.toml`

Why it exists: owns backend runtime/development dependencies and pytest discovery.

What it does: declares only Django, DRF, Psycopg, pytest, and pytest-django direct dependencies for this slice.

What it does not do: it does not add formatters, linters, workers, schedulers, brokers, caches, Connector libraries, or frontend dependencies.

### `backend/uv.lock`

Why it exists: provides ADR-002 exact reproducible dependency state.

What it does: locks the complete compatible dependency graph.

What it does not do: lock state alone does not claim supply-chain or vulnerability approval.

### `backend/tests/configuration/test_configuration.py`

Why it exists: verifies the slice's deterministic configuration behavior independently of Docker/PostgreSQL.

What it does: tests defaults, overrides, required secrets, placeholder rejection, strict booleans, port ranges, and secret-safe representations.

What it does not do: it contains no domain, API, authentication, authorization, migration, or persistence behavior tests.

### `docs/implementation/INSTALLATION.md`

Records every dependency-installation/setup command, purpose, affected manifest/lock files, and resolved version.

### `docs/implementation/RUN.md`

Records every developer command needed to configure, check, test, run, and stop this backend foundation and its existing PostgreSQL service.

### `docs/implementation/DATABASE.md`

Records the database connection profile, non-destructive inspection commands and queries, migration ownership rule, and Docker runtime blocker.

### `docs/implementation/COMMAND-LOG.md`

Records materially relevant terminal commands executed during this slice, including failures and environment warnings.

## Explicitly deferred

- `pipelines` Django application and all domain/application/infrastructure/API packages
- PipelineDefinition, PipelineDefinitionId, registration and inspection use cases
- ORM models, migrations, serializers, views, API routes, and `nexetl_pipeline_definition`
- Authentication and CSRF endpoint implementation
- Capability authorization implementation
- External error catalogue/translation implementation
- Frontend work
- Production deployment, secret provider, runtime, scheduling, worker, broker, cache, Connector, and Extension implementation
