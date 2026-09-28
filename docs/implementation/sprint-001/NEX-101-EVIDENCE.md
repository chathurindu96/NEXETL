# NEX-101 Evidence

## Ticket

NEX-101 — Establish Django Project and Composition Bootstrap.

## Work Package

WP-02 — Backend/Django Bootstrap Foundation.

## Governed Sources

- NEXETL-PLAN-001 v0.1, WP-02.
- NEXETL-DES-001 v1.0, backend module mapping, Django bootstrap/composition,
  repository structure, and dependency rules.
- NEXETL-DOC-016, NEXETL-DOC-020, NEXETL-DOC-023, NEXETL-DOC-024, and
  NEXETL-DOC-025.
- Accepted NEXETL-ADR-001 and NEXETL-ADR-002.
- `docs/agile/tickets/sprint-001/NEX-101-establish-django-project-and-composition-bootstrap.md`.

## Initial State

The existing WP-01 foundation already contained `backend/manage.py`, the
`backend/src/nexetl/` bootstrap package, Django settings, root URLs, ASGI and
WSGI entry points, a committed uv lock, and implementation documentation.
There was no `pipelines` package, domain behavior, ORM model, migration, or
business API route.

## Gap Assessment

| Requirement / Criterion | Initial State | Action | Final State |
|---|---|---|---|
| Django initializes with valid controlled configuration and reports no system-check issues | PARTIAL: existing command evidence only | Ran the controlled system check | PASS |
| Bootstrap owns composition only, with no Pipeline Definition business implementation | PASS | Re-inspected source and package tree | PASS |
| Existing repository evidence is reused rather than duplicated | PARTIAL: no dedicated bootstrap import smoke test | Added one focused import smoke test | PASS |
| ASGI and WSGI entry points load as minimal framework adapters | PARTIAL: source review only | Added import coverage in the focused smoke test | PASS |

## Files Changed

- Source: none.
- Tests: `backend/tests/bootstrap/test_django_bootstrap.py`.
- Dependency/lock: none.
- Documentation: this evidence file, `docs/implementation/COMMAND-LOG.md`, and
  `docs/implementation/backend-foundation.md`.

## Commands Executed

See `docs/implementation/COMMAND-LOG.md` for the command record, including a
failed shell-quoting attempt and its separate retries. Temporary controlled
configuration values were process-local and are not recorded.

## Verification Results

- `uv lock --check --offline`: PASS; 16 packages resolved from the committed
  lock state.
- `uv sync --locked --dry-run --offline`: PASS; 15 packages checked and no
  changes would be made.
- Django system check: PASS; no issues identified.
- Bootstrap import/startup checks: covered by the NEX-101 smoke test.
- Focused configuration baseline: PASS; 18 tests passed before the NEX-101
  smoke test was added.

## Acceptance Criteria Assessment

| Acceptance criterion | Result | Evidence |
|---|---|---|
| With valid controlled configuration Django initializes and system check reports no issues | PASS | Controlled `manage.py check` result in `COMMAND-LOG.md` |
| The bootstrap package owns composition only and contains no Pipeline Definition business implementation | PASS | Package-tree and source review; focused smoke test confirms intentionally empty root URLs |
| Current repository evidence is reused or verified rather than duplicated | PASS | Existing shell retained; one missing focused import test added |

## Out-of-Scope Verification

- NEX-102 was not started.
- NEX-103 was not started.
- WP-03 implementation was not changed or pulled forward.
- PipelineDefinition implementation was not started.
- No migrations were introduced.
- No API business endpoints were introduced.

## Remaining Follow-Up

- NEX-102 owns the `pipelines` package and layer-boundary implementation.
- NEX-103 owns application and feature routing foundations.
- NEX-104 owns broader dependency-boundary verification.
