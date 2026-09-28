# NEX-107 — Configure PostgreSQL Bootstrap Environment Mapping

## Metadata
- Type: TASK
- Epic / Parent WP: WP-03 — Configuration and Startup Validation
- Sprint: Sprint 1 candidate
- Priority: P1
- Story Points: 3
- Component: Database
- Status: Candidate for commitment
- Dependencies: NEX-105, NEX-106; WP-01 Compose asset

## User / Engineering Value
Consistent environment mapping lets Django and local Compose refer to PostgreSQL safely without hard-coded credentials or premature schema work.

## Background
DES-001 defines DB name, user, password, host, and port ownership/default/validation. WP-04 owns live connectivity and persistence foundation, so this ticket is configuration mapping only.

## Problem Statement
Backend and Compose configuration names must align so later database work has one explicit, documented contract.

## Scope
- Map governed DB environment values into Django database settings.
- Verify names and safe defaults align with Compose and example configuration.
- Keep password mandatory and protected.

## Out of Scope
- Starting PostgreSQL as an acceptance dependency, connectivity implementation, migrations, tables, SQL, ORM models, sessions, or WP-04 completion.

## Governed Sources
- PLAN-001 §9, WP-03; WP-04 boundary in §10.
- DES-001 §§9, 15.2, 15.4–15.5, 20.1–20.6, 21.9.
- ADR-006; DOC-020, DOC-024.

## Requirements Traceability
- NEXETL-REQ-004 — Retain Pipeline Definition (enabling configuration only).
- NEXETL-REQ-095 — Secret Confidentiality.
- NEXETL-REQ-113 — Controlled Configuration.
- NEXETL-REQ-119 — Containerized Deployment Portability.
- NEXETL-REQ-120 — Environment-Specific Dependency Governance.

## Technical Design Constraints
- Django uses PostgreSQL, not SQLite fallback.
- Local host/port defaults are approved local-profile values; password has no default.
- Compose binds PostgreSQL to loopback; port conflicts are configuration concerns, not permission to broaden exposure.

## Implementation Tasks
- [ ] Compare Django, Compose, and example-environment variable names.
- [ ] Reconcile mapping within the governed configuration boundary.
- [ ] Verify rendered Django database settings using redacted assertions.
- [ ] Confirm no connection, migration, or schema action occurs.
- [ ] Document local port override behavior safely.

## Files / Areas Expected to Change
- Human-maintained: `backend/src/nexetl/configuration.py`, `backend/src/nexetl/settings.py`, `.env.example`, `compose.yaml` only if evidence shows a mapping defect.
- Generated: none expected.

Before modifying code, perform an impact assessment. Keep the change in its owning boundary. If it unexpectedly requires manual changes across many unrelated files, **STOP** and report the large blast radius, duplicated knowledge, leaking boundaries, and whether the cause is implementation debt, DES ambiguity, or architecture contradiction. Do not perform shotgun surgery to make tests pass; report generated and human-maintained files separately.

## Installation Impact
- Packages expected: psycopg binary support only if absent from the governed lock.
- Installation commands: governed uv command only if required.
- `INSTALLATION.md`: update for any actual driver/install change.

## Runtime Command Impact
- `RUN.md` must explain the DB environment inputs and host-port override when applicable.

## Database Impact
- Configuration only. No migration, query, SQL, schema, or database object change.

## Security Considerations
- DB password is required, external, redacted, and never committed; local published port remains loopback-only.

## Error / Failure Considerations
- Missing password or malformed port fails before connection; connection refusal belongs to later runtime verification and must remain distinguishable.

## Test Requirements
- Configuration tests for defaults, overrides, redaction, engine selection, and port validation; no live DB test.

## Documentation Requirements
- Update `DATABASE.md`, `RUN.md`, `INSTALLATION.md` if needed, `COMMAND-LOG.md`, and traceability.

## Acceptance Criteria
- [ ] Django database settings resolve to the PostgreSQL backend with governed values.
- [ ] Compose/example/backend names are consistent or an explicit governed discrepancy is raised.
- [ ] No database connection, SQL, migration, or schema work is introduced.

## Definition of Done
- [ ] Project DoD is satisfied with redacted mapping evidence and WP-04 boundary review.

## Evidence Required
- Configuration test output, redacted settings assertion, Compose configuration output if inspected, focused Git diff.

## Risks / Notes
- Host port availability varies; overrides must not alter the container’s internal PostgreSQL port or expose it beyond loopback.

## Blocking Conditions
Stop for a DES/config-name contradiction, requested SQLite fallback, secret exposure, or any requirement to begin WP-04 persistence work.
