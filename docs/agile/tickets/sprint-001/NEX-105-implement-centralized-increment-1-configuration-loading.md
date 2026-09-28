# NEX-105 — Implement Centralized Increment 1 Configuration Loading

## Metadata
- Type: STORY
- Epic / Parent WP: WP-03 — Configuration and Startup Validation
- Sprint: Sprint 1 candidate
- Priority: P1
- Story Points: 5
- Component: Configuration
- Status: Candidate for commitment
- Dependencies: NEX-101

## User / Engineering Value
Centralized, typed configuration makes environment differences explicit and prevents configuration knowledge from leaking through application code.

## Background
ADR-006 and DES-001 require one semantic owner per concern, explicit process-environment sources, safe defaults only where approved, and separate secret handling.

## Problem Statement
Increment 1 settings need one reviewable resolution boundary rather than scattered environment reads and implicit defaults.

## Scope
- Load the DES-001 backend configuration set centrally.
- Represent values with explicit types and ownership.
- Apply only approved local defaults and keep secrets mandatory.
- Supply resolved values to Django settings.

## Out of Scope
- Startup-failure catalogue beyond NEX-106, frontend configuration, production secret-manager selection, authentication behavior, and Pipeline business behavior.

## Governed Sources
- PLAN-001 §9, WP-03.
- DES-001 §§15.1–15.4 and 20.5.
- ADR-006; DOC-020 and DOC-023.

## Requirements Traceability
- NEXETL-REQ-095 — Secret Confidentiality.
- NEXETL-REQ-112 — Explicit Responsibility Boundaries.
- NEXETL-REQ-113 — Controlled Configuration.
- NEXETL-REQ-114 — Governed Change Traceability.
- NEXETL-REQ-120 — Environment-Specific Dependency Governance.

## Technical Design Constraints
- Domain/application code must not read process environment directly.
- Secret key and DB password have no fallback.
- Preserve DES-001 setting names/defaults; do not silently rename or broaden them.
- Do not infer secure-cookie values from debug mode.

## Implementation Tasks
- [ ] Reconcile existing configuration code and names against DES-001.
- [ ] Define the centralized typed configuration representation.
- [ ] Implement approved source/default resolution without validation duplication.
- [ ] Wire resolved values into Django settings.
- [ ] Audit the backend for scattered environment reads.

## Files / Areas Expected to Change
- Human-maintained: `backend/src/nexetl/configuration.py`, `backend/src/nexetl/settings.py`, `.env.example` only for safe names/examples.
- Generated: none expected.

Before modifying code, perform an impact assessment. Keep the change in its owning boundary. If it unexpectedly requires manual changes across many unrelated files, **STOP** and report the large blast radius, duplicated knowledge, leaking boundaries, and whether the cause is implementation debt, DES ambiguity, or architecture contradiction. Do not perform shotgun surgery to make tests pass; report generated and human-maintained files separately.

## Installation Impact
- Packages expected: none; do not introduce dotenv or a settings framework without governed justification.
- Installation commands: none.
- `INSTALLATION.md`: update for environment setup, not package installation, if required.

## Runtime Command Impact
- `RUN.md` must show required environment inputs and safe local overrides without real secrets.

## Database Impact
- Configuration only; no connection verification, query, migration, or schema change.

## Security Considerations
- Secret values must not appear in representations, errors, logs, docs, tests, or committed examples.

## Error / Failure Considerations
- Unresolved mandatory inputs are handed to the centralized validation path and fail safely before readiness.

## Test Requirements
- Unit/configuration tests for source resolution, defaults, types, secret redaction, and absence of scattered environment reads.

## Documentation Requirements
- Update `INSTALLATION.md`, `RUN.md`, `COMMAND-LOG.md`, and configuration traceability; update `DATABASE.md` for connection variables only.

## Acceptance Criteria
- [ ] Every DES-001 backend setting has one semantic owner and centralized source.
- [ ] Only approved local defaults are applied; mandatory secrets have none.
- [ ] Domain/application packages contain no raw environment reads.
- [ ] Documentation contains names and safe examples but no real secret.

## Definition of Done
- [ ] Project DoD is satisfied and the configuration inventory is traceable to ADR-006/DES-001.

## Evidence Required
- Configuration test output, environment-read audit, focused Git diff, redacted documentation evidence.

## Risks / Notes
- Current code may contain a DES-001 naming mismatch; do not silently choose a spelling—confirm the controlled design and treat a material contradiction through governance.

## Blocking Conditions
Stop for inconsistent governed setting names that materially change the contract, a request for unsafe defaults, a secret-handling contradiction, or unexpected broad coupling.
