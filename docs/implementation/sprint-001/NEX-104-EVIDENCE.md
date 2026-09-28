# NEX-104 Evidence

## Ticket

NEX-104 — Add Backend Bootstrap and Dependency-Boundary Verification Tests.

## Work Package

WP-02 — Backend/Django Bootstrap Foundation.

## Governed Sources

- NEXETL-PLAN-001 v0.1, WP-02.
- NEXETL-DES-001 v1.0, backend dependency direction, composition, and test
  expectations.
- NEXETL-DOC-016, NEXETL-DOC-023, and NEXETL-DOC-025.
- Accepted NEXETL-ADR-001 and NEXETL-ADR-002.
- NEX-101, NEX-102, and NEX-103 evidence records.
- `docs/agile/tickets/sprint-001/NEX-104-add-backend-bootstrap-and-dependency-boundary-verification-tests.md`.

## Existing Test Inventory

| Existing Test Area | Coverage | NEX-104 Action |
|---|---|---|
| `test_django_bootstrap.py` | Django settings, root URL import, ASGI/WSGI import | REUSED |
| `test_pipeline_package_boundaries.py` | Package imports, app registration, basic framework-independence | REUSED |
| `test_url_composition.py` | Empty `/api/` seam and absent future routes | REUSED |
| `test_configuration.py` | Deterministic controlled configuration | NO CHANGE |
| `test_architecture_dependency_boundaries.py` | Full approved layer directions, cycle guard, violation proof | NEW |

## Dependency Rules Enforced

- `domain` may not import Django, DRF, application, infrastructure, or API.
- `application` may not import Django ORM (`django.db`), DRF, infrastructure,
  or API. The guard intentionally does not prohibit every possible Django
  symbol because the governed rule is specifically against ORM/DRF and
  infrastructure concerns.
- `infrastructure` may not import API.
- `api` has no outward layer dependency rule beyond the existing governed
  design; later adapters may depend inward on application/domain.
- Absolute `pipelines.*` layer imports are converted to a graph and checked for
  architecture-layer cycles.

## Verification Mechanism

The test discovers Python files in each governed package, parses each with the
standard-library `ast` module, and evaluates actual `Import` and `ImportFrom`
nodes against explicit forbidden-prefix rules. It is deterministic, reports the
source layer, file, and prohibited import, and does not rely on raw substring
matching. No new architecture-analysis dependency or production framework was
introduced.

## Violation-Detection Proof

A synthetic application module containing
`from pipelines.infrastructure import persistence` produces the explicit
application-to-infrastructure violation message. A synthetic two-layer graph
also produces deterministic cycle reports in both traversal directions.

## Files Changed

- Production source: none.
- Test: `backend/tests/bootstrap/test_architecture_dependency_boundaries.py`.
- Configuration: none.
- Documentation: this evidence file, `docs/implementation/COMMAND-LOG.md`,
  and `docs/implementation/backend-foundation.md`.
- Dependencies: none.

## Commands Executed

See `docs/implementation/COMMAND-LOG.md`. No command starts PostgreSQL,
Docker, migrations, or SQL.

## Focused Verification Results

`uv run --offline pytest tests\bootstrap\test_architecture_dependency_boundaries.py`:
PASS — four tests passed.

## Full Backend Test Results

`uv run --offline pytest`:
PASS — 30 tests passed; no failures or skips.

## Django System Check

`uv run --offline python manage.py check`:
PASS — no issues identified.

## Database Independence

All NEX-104 tests ran without PostgreSQL, Docker, migrations, schema creation,
or SQL. They use source inspection and controlled Django bootstrap only.

## Acceptance Criteria Assessment

| Acceptance criterion | Result | Evidence |
|---|---|---|
| Bootstrap verification is repeatable | PASS | Existing bootstrap tests plus complete suite |
| Dependency-direction checks are effective | PASS | AST inspection over all four packages |
| A forbidden dependency is demonstrably detected | PASS | Synthetic outward-dependency test |
| Tests run without PostgreSQL | PASS | Focused and full suite results |
| Full backend tests and Django system check pass | PASS | 30 tests passed; system check clean |
| No later functionality is introduced | PASS | Source/diff review |

## Out-of-Scope Verification

- No PipelineDefinition implementation, ORM model, migration, or endpoint was
  introduced.
- No authentication, authorization, configuration/WP-03, or frontend work was
  introduced.
- No production source, dependency, or pytest-configuration file changed.

## Follow-Up

- NEX-105 owns centralized configuration implementation.
- Later work packages own domain behavior, persistence, security, error, and
  REST operations.
