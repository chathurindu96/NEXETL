# NEX-106 Evidence — Startup Configuration Validation and Safe Failure Handling

## Ticket

NEX-106 — Implement Startup Configuration Validation and Safe Failure Handling

## Work Package

WP-03 — Configuration and Startup Validation

## Governed Sources

- NEXETL-PLAN-001 v0.1 — Approved, WP-03
- NEXETL-DES-001 v1.0 — Approved, §§15.1–15.5, 19.6, 21.8, 22.1–22.2
- NEXETL-ADR-006 — Accepted
- NEXETL-DOC-020 and NEXETL-DOC-023 — Approved

## Initial Validation Inventory

| Concern | Governed rule | Initial state | Action | Final state |
|---|---|---|---|---|
| Django secret key | present, non-empty, no placeholder | PARTIAL | central secret validation | PASS |
| DB password | present, non-empty, no placeholder | PARTIAL | central secret validation | PASS |
| DB name/user/host | non-empty | PARTIAL | central text validation | PASS |
| DB port | integer 1–65535 | PARTIAL | controlled conversion and range validation | PASS |
| Debug/cookie flags | strict booleans | PARTIAL | controlled boolean conversion failure | PASS |
| Allowed hosts | parsed non-empty host list | MISSING | central list validation | PASS |
| PostgreSQL configuration | complete before readiness | MISSING | validate all resolved database fields | PASS |

## Validation Architecture

`load_backend_configuration()` resolves typed values only. `validate_backend_configuration()` validates the resolved configuration, and `nexetl.settings` consumes only the validated result. Invalid configuration therefore prevents Django readiness before any database configuration can be used.

## Controlled Failure Type

`ConfigurationError` is the sole internal startup-configuration failure type. Its messages identify the affected setting and corrective condition without rendering supplied secret values, the environment, or a full configuration object.

## Validation Rules

| Setting / concern | Validation | Failure behaviour |
|---|---|---|
| Django secret key / DB password | supplied, non-blank, not a known documentation placeholder | `ConfigurationError` |
| DB name, user, host | non-empty after resolution | `ConfigurationError` |
| DB port | integer in 1–65535 | `ConfigurationError` |
| Debug and secure-cookie flags | only `true` or `false` | `ConfigurationError` |
| Allowed hosts | resolves to at least one host | `ConfigurationError` |

## Secret Safety

Secret fields remain excluded from configuration representations. Tests verify that controlled errors and subprocess startup output omit synthetic supplied values. No environment dump, secret logging, or external API error contract was added.

## Negative and Boundary Tests

The focused test suite covers missing, empty, whitespace, and placeholder secrets; empty DB text settings; malformed and boundary database ports (1 and 65535 valid; 0 and 65536 invalid); strict booleans; empty allowed-host representations; complete valid configuration; and a non-zero safe Django startup failure proof.

## Startup Evidence

An isolated `manage.py check` subprocess with invalid configuration exited non-zero, named the failing setting, and omitted the supplied placeholder. A valid controlled configuration completed Django's system check successfully.

## Test Results

- Focused configuration validation: 52 passed.
- Bootstrap regression: 12 passed.
- Architecture-boundary regression: 4 passed.
- Full backend suite: 64 passed.
- Django system check: passed.

## Files Changed

- Production: `backend/src/nexetl/configuration.py`, `backend/src/nexetl/settings.py`
- Tests: `backend/tests/configuration/test_configuration.py`
- Documentation: this evidence file, `RUN.md`, `COMMAND-LOG.md`, and `backend-foundation.md`
- Dependencies/configuration: none

## Database Independence

PostgreSQL was not started. No connection, SQL, migration, or schema operation occurred. Validation is configuration coherence only, not database reachability.

## Acceptance Criteria Assessment

| Criterion | Result |
|---|---|
| Invalid governed configuration fails safely before readiness | PASS |
| Valid configuration allows Django checks | PASS |
| DES-001 §15.5 categories are covered by deterministic tests | PASS |

## Out-of-Scope Verification

No NEX-107 database bootstrap/connectivity work, WP-09 external error contract, health endpoint, authentication/authorization implementation, Pipeline Definition implementation, REST business endpoint, frontend work, dependency addition, or migration was introduced.

## Follow-Up

NEX-107 remains the owner of subsequent PostgreSQL bootstrap/connectivity work.
