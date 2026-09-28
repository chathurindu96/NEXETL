# NEX-103 Evidence

## Ticket

NEX-103 — Establish Django/DRF URL and Application Bootstrap Foundation.

## Work Package

WP-02 — Backend/Django Bootstrap Foundation.

## Governed Sources

- NEXETL-PLAN-001 v0.1, WP-02.
- NEXETL-DES-001 v1.0 §§6.1–6.3, 7.1–7.2, 11.5, and 12.6.
- NEXETL-DOC-016, NEXETL-DOC-017, NEXETL-DOC-020, NEXETL-DOC-023,
  NEXETL-DOC-024, and NEXETL-DOC-025.
- Accepted NEXETL-ADR-001, NEXETL-ADR-003, NEXETL-ADR-004, and NEXETL-ADR-007.
- `docs/agile/tickets/sprint-001/NEX-103-establish-django-drf-url-and-application-bootstrap-foundation.md`.

## Initial State

Django and Django REST Framework were already direct locked dependencies and
`rest_framework` was already registered. The root URL module existed but had
an empty route list; `pipelines.api` had no URL composition module.

## Gap Assessment

| Criterion | Initial State | Action | Final State |
|---|---|---|---|
| Django and DRF initialize under controlled configuration | PASS | Reused existing dependency and registration | PASS |
| Root URLs resolve without WP-07+ or WP-10 routes | PARTIAL | Added empty `/api/` composition seam | PASS |
| No business serializer, view, route, or error contract is implemented | PASS | Added negative URL-resolution coverage | PASS |

## DRF Dependency Decision

**Already available.** `djangorestframework>=3.18.1` is declared in
`backend/pyproject.toml`, locked in `backend/uv.lock`, and `rest_framework` is
already registered in Django settings. No dependency installation or lock-file
change was needed.

## URL Composition Design

`nexetl.urls` owns the root composition boundary and explicitly includes
`pipelines.api.urls` under `/api/`. `pipelines.api.urls` is intentionally
empty: it is the future feature-routing seam, not an endpoint implementation.

No Pipeline Definition, CSRF, authentication, authorization, error-translation,
or versioned API behavior is routed by this ticket.

## Files Changed

- Source: `backend/src/nexetl/urls.py` and `backend/src/pipelines/api/urls.py`.
- Tests: `backend/tests/bootstrap/test_url_composition.py` and the compatible
  empty-seam assertion update in `test_django_bootstrap.py`.
- Dependency/lock: none.
- Documentation: this evidence file, `docs/implementation/COMMAND-LOG.md`,
  and `docs/implementation/backend-foundation.md`.

## Commands Executed

See `docs/implementation/COMMAND-LOG.md`. Controlled process-only
configuration values are not recorded.

## Verification Results

- Complete bootstrap suite: PASS — eight tests passed.
- Django system check: PASS — no issues identified.
- Root resolver inventory: one `/api/` resolver with an empty child route list.
- Negative resolution: `/api/pipeline-definitions/`,
  `/api/pipeline-definitions/{id}/`, and `/api/security/csrf/` each raise
  `Resolver404`.

## Route Inventory

| Route surface | State |
|---|---|
| `/api/` | Empty composition resolver only |
| `/api/pipeline-definitions/` | Absent |
| `/api/pipeline-definitions/{pipelineDefinitionId}/` | Absent |
| `/api/security/csrf/` | Absent |

## Acceptance Criteria Assessment

| Acceptance criterion | Result | Evidence |
|---|---|---|
| Django and DRF initialize with valid controlled configuration | PASS | Bootstrap suite and Django system check |
| Root URL configuration resolves without exposing WP-07+ or WP-10 routes | PASS | Resolver inventory and negative route tests |
| No business serializer, view, route, or error contract is implemented | PASS | Focused source review and negative route tests |

## Out-of-Scope Verification

- No PipelineDefinition endpoint, serializer, business view, or ViewSet exists.
- No CSRF endpoint implementation exists.
- No authentication, authorization, or error-contract implementation exists.
- No migration or database action occurred.
- No frontend work occurred.

## Follow-Up Ownership

- NEX-104 owns broader dependency-boundary verification.
- WP-07 owns CSRF and session-authentication behavior.
- WP-09 owns centralized error translation.
- WP-10 owns Pipeline Definition REST operations.
