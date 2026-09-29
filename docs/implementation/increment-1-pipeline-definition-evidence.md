# Increment 1 — Pipeline Definition Component Evidence

## Delivered behavior

The SvelteKit registration view bootstraps CSRF, posts to Django/DRF, and
navigates to inspection. The backend authorizes before lookup, generates a UUID
v4 identity, and persists it through the Django PostgreSQL adapter. The public
API exposes only the governed `id` field.

## Verification

- Backend: 86 tests passed; PostgreSQL-backed API integration tests passed;
  system check passed; migration consistency reports no model changes.
- Frontend: 11 Vitest tests passed; Svelte diagnostics passed with no warnings;
  production build passed.
- API/OpenAPI: the three governed operations and stable error shape are in
  `openapi/increment-1.yaml`.

## Authentication-first Product Owner extension

The Product Owner explicitly authorized a narrowly scoped extension beyond the
original Increment 1 visual baseline: an authentication-first local browser
experience and an opt-in development-only Django superadmin bootstrap. The
backend remains authoritative for authentication, session validity, CSRF, and
Pipeline permissions; frontend route gating is UX only.

The real session API provides CSRF-protected login/logout and a browser-safe
session-state response. The `bootstrap_dev_superadmin` command is idempotent,
uses Django password hashing, and refuses unless both `DEBUG=true` and
`NEXETL_DEV_SUPERADMIN_ENABLED=true` are present. `admin / 123` is disabled by
default and is DEVELOPMENT-ONLY: it must never be enabled for production,
untrusted staging, or public deployment. No custom user model, automatic
account creation, authentication bypass, OAuth/OIDC/SSO, or username-specific
authorization rule was introduced.

Unauthenticated browser users are routed to `/login` before the application
shell. Authenticated users receive the compact Pipeline workspace, can create
the governed UUID-only Pipeline Definition, inspect its persisted ID, and sign
out through the real Django session. Expired or invalid API sessions clear the
safe client session state and return the user to login.

## Infrastructure and E2E status

The NEXETL Compose database is reachable on `127.0.0.1:5433`; migrations were
applied from the ignored root `.env`. Read-only inspection confirms the
Pipeline Definition table has exactly the governed UUID primary key column.
The previous browser-login blocker is removed. The governed Playwright and
axe-core test layer now verifies the real browser flow: unauthenticated route
redirect, CSRF-protected Django login, Pipeline registration, inspection of the
same persisted UUID, logout, and protected-route redirect. Login and workspace
pages have no critical axe violations. The local SvelteKit origin is explicitly
configured through `NEXETL_CSRF_TRUSTED_ORIGINS`; it defaults to no trusted
cross-origin callers. No authentication or CSRF bypass was introduced.

## Runtime usability and observability

The backend root returns a safe non-business service index, and the frontend
root routes users to registration. SvelteKit provides a friendly unknown-route
page and a local favicon. Backend request logs include only method, path,
status, and duration; API exceptions remain externally sanitized.

## Frontend visual foundation

The frontend has a tokenized global style entry point, responsive authenticated
shell, restrained sidebar/top bar, compact user area and sign-out control, and
small shared UI primitives. The dedicated login layout does not render the
workspace sidebar. Registration and inspection retain the governed
identity-only Pipeline behavior while presenting the refined application shell.
