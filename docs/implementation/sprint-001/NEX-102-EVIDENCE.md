# NEX-102 Evidence

## Ticket

NEX-102 — Establish Pipeline Backend Package and Layer Boundaries.

## Work Package

WP-02 — Backend/Django Bootstrap Foundation.

## Governed Sources

- NEXETL-PLAN-001 v0.1, WP-02.
- NEXETL-DES-001 v1.0 §§6.1–6.5 and 7.1–7.2.
- NEXETL-DOC-016, NEXETL-DOC-023, NEXETL-DOC-024, and NEXETL-DOC-025.
- Accepted NEXETL-ADR-001 and NEXETL-ADR-002.
- `docs/agile/tickets/sprint-001/NEX-102-establish-pipeline-backend-package-and-layer-boundaries.md`.

## Initial State

The NEX-101 `nexetl` composition/bootstrap package existed and passed its
verification, but `backend/src/pipelines/` did not exist. No Pipeline
Definition domain behavior, application behavior, ORM model, migration, or
feature endpoint existed.

## Package Structure Created

```text
backend/src/pipelines/
├── __init__.py
├── apps.py
├── domain/__init__.py
├── application/__init__.py
├── infrastructure/__init__.py
└── api/__init__.py
```

## Layer Responsibility Mapping

| Package | Responsibility | Allowed Dependencies | Forbidden Dependencies |
|---|---|---|---|
| `pipelines.domain` | Framework-independent Pipeline Definition meaning | Standard-library and future domain-only contracts | Django, DRF, ORM, application, infrastructure, API |
| `pipelines.application` | Future use-case coordination and ports | Domain | Django ORM, DRF, infrastructure, API |
| `pipelines.infrastructure` | Future technical adapters | Application/domain contracts where justified | API |
| `pipelines.api` | Future DRF/HTTP delivery adapter | Application/domain contracts where justified | Domain semantics and direct ORM access |

## Django App Registration Decision

**Required now.** DES-001 §6.1 explicitly defines one domain-aligned Django
application named `pipelines`, and its approved repository structure includes
`pipelines/apps.py`. `pipelines.apps.PipelinesConfig` is therefore registered
in `nexetl.settings.INSTALLED_APPS`. No separate Django app was created for
technical concerns.

## Files Changed

- Source: `backend/src/pipelines/__init__.py`, `apps.py`, and the four package
  markers; `backend/src/nexetl/settings.py` for the required app registration.
- Tests: `backend/tests/bootstrap/test_pipeline_package_boundaries.py`.
- Documentation: this evidence file, `docs/implementation/COMMAND-LOG.md`,
  and `docs/implementation/backend-foundation.md`.
- Dependency/lock: none.

## Tests and Checks

- Focused structural tests: PASS — three tests passed.
- Django system check with controlled process configuration: PASS — no issues
  identified.
- The first focused test run found a test-fixture omission of
  `DJANGO_SETTINGS_MODULE`; it was corrected in the test fixture and rerun
  successfully. No application code was changed to address it.

## Acceptance Criteria Assessment

| Acceptance criterion | Result | Evidence |
|---|---|---|
| Four DES-001 package boundaries exist and import under test configuration | PASS | Focused import and Django app-registration test |
| Domain/application contain no Django ORM or DRF dependency | PASS | AST-based focused structural check over both packages |
| No WP-05+ business behavior or speculative abstraction is introduced | PASS | Package-tree/source review and focused Git diff |
| Dependency rules are reviewable and repeatable | PASS | Layer table and focused structural tests |

## Out-of-Scope Verification

- No domain entity was created.
- No use case was created.
- No port was created; only empty package boundaries were introduced.
- No ORM model or migration was introduced.
- No API endpoint, serializer, view, ViewSet, or feature route was introduced.
- No authentication, authorization, CSRF, error-translation, OpenAPI, or
  frontend implementation was introduced.

## Remaining Follow-Up

- NEX-103 owns application and feature routing foundations.
- NEX-104 owns broader dependency-direction verification.
- NEX-105 and later tickets own configuration and subsequent behavior.
