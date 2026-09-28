# Increment 1 — Pipeline Definition Component Evidence

## Delivered behavior

The SvelteKit registration view bootstraps CSRF, posts to Django/DRF, and
navigates to inspection. The backend authorizes before lookup, generates a UUID
v4 identity, and persists it through the Django PostgreSQL adapter. The public
API exposes only the governed `id` field.

## Verification

- Backend: 75 tests passed; system check passed; migration consistency reports
  no model changes.
- Frontend: 7 Vitest tests passed; Svelte diagnostics passed with no warnings;
  production build passed.
- API/OpenAPI: the three governed operations and stable error shape are in
  `openapi/increment-1.yaml`.

## Infrastructure exception

The NEXETL Compose database is reachable on `127.0.0.1:5433` and contains no
application tables. The host process has no `NEXETL_DB_PASSWORD`; port `5432`
is occupied by an unrelated local PostgreSQL process. Therefore migration
application and browser E2E were not claimed. The private Compose database
password and an explicit `NEXETL_DB_PORT=5433` are required for those checks.
