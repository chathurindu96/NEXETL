# Increment 1 — Pipeline Definition Component Evidence

## Delivered behavior

The SvelteKit registration view bootstraps CSRF, posts to Django/DRF, and
navigates to inspection. The backend authorizes before lookup, generates a UUID
v4 identity, and persists it through the Django PostgreSQL adapter. The public
API exposes only the governed `id` field.

## Verification

- Backend: 79 tests passed; PostgreSQL-backed API integration tests passed;
  system check passed; migration consistency reports no model changes.
- Frontend: 7 Vitest tests passed; Svelte diagnostics passed with no warnings;
  production build passed.
- API/OpenAPI: the three governed operations and stable error shape are in
  `openapi/increment-1.yaml`.

## Infrastructure exception

The NEXETL Compose database is reachable on `127.0.0.1:5433`; migrations were
applied from the ignored root `.env`. Read-only inspection confirms the
Pipeline Definition table has exactly the governed UUID primary key column.
Browser E2E is not configured: no Playwright/axe setup exists, and the approved
Increment 1 API has no browser login operation. No authentication or CSRF
bypass was introduced merely to simulate that flow.
