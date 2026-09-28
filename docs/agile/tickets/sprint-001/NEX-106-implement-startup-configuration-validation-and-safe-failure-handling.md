# NEX-106 — Implement Startup Configuration Validation and Safe Failure Handling

## Metadata
- Type: STORY
- Epic / Parent WP: WP-03 — Configuration and Startup Validation
- Sprint: Sprint 1 candidate
- Priority: P1
- Story Points: 5
- Component: Configuration
- Status: Candidate for commitment
- Dependencies: NEX-105

## User / Engineering Value
Fail-fast validation prevents the service from appearing ready with unsafe or incoherent settings and gives operators actionable, non-sensitive diagnostics.

## Background
DES-001 §15.5 requires validation before backend readiness for required secrets, port, hosts, strict booleans, and complete DB settings.

## Problem Statement
Resolved text values are insufficient unless invalid and missing configuration is rejected consistently without leaking secrets.

## Scope
- Validate required values, strict booleans, non-empty host lists, port range, and complete DB settings.
- Raise one controlled configuration failure type before Django readiness.
- Redact protected values from representations and diagnostics.

## Out of Scope
- External API error catalogue, production health endpoints, database connectivity, authentication behavior, and generalized configuration framework.

## Governed Sources
- PLAN-001 §9, WP-03.
- DES-001 §§15.1–15.5, 19.6, 21.8, 22.1–22.2.
- ADR-006; DOC-020 and DOC-023.

## Requirements Traceability
- NEXETL-REQ-095 — Secret Confidentiality.
- NEXETL-REQ-098 — Fail-Safe Security Behavior.
- NEXETL-REQ-109 — Actionable Diagnostic Information.
- NEXETL-REQ-113 — Controlled Configuration.
- NEXETL-REQ-117 — Deterministic Testability.

## Technical Design Constraints
- Validation is centralized and deterministic.
- Reject known placeholders and malformed values; do not coerce ambiguous booleans.
- Diagnostics identify the setting/problem but never its secret value.

## Implementation Tasks
- [ ] Inventory required validation rules against DES-001.
- [ ] Implement or reconcile centralized validators and failure type.
- [ ] Add redaction-safe representations and messages.
- [ ] Test every missing/invalid branch and valid boundary values.
- [ ] Confirm failure occurs before readiness or database activity.

## Files / Areas Expected to Change
- Human-maintained: `backend/src/nexetl/configuration.py`, configuration tests, limited bootstrap wiring if needed.
- Generated: test caches only; ignored.

Before modifying code, perform an impact assessment. Keep the change in its owning boundary. If it unexpectedly requires manual changes across many unrelated files, **STOP** and report the large blast radius, duplicated knowledge, leaking boundaries, and whether the cause is implementation debt, DES ambiguity, or architecture contradiction. Do not perform shotgun surgery to make tests pass; report generated and human-maintained files separately.

## Installation Impact
- Packages expected: none.
- Installation commands: none.
- `INSTALLATION.md`: update only for clarified startup prerequisites.

## Runtime Command Impact
- `RUN.md` must describe safe expected failure and a valid startup example with placeholders.

## Database Impact
- Configuration only; no query, migration, or schema change.

## Security Considerations
- Fail closed; never echo secret key or DB password; do not log the full environment.

## Error / Failure Considerations
- Missing secret, placeholder secret, invalid port/boolean/hosts, and incomplete DB settings must produce stable internal configuration failures and non-zero startup.

## Test Requirements
- Configuration unit tests for all positive, negative, boundary, precedence, and redaction cases; Django check with valid inputs.

## Documentation Requirements
- Update `RUN.md`, `INSTALLATION.md` where needed, `COMMAND-LOG.md`, and implementation traceability.

## Acceptance Criteria
- [ ] Given any invalid governed setting, startup fails before readiness with no sensitive value in output.
- [ ] Given valid settings, configuration resolution is deterministic and Django checks can proceed.
- [ ] Tests cover every DES-001 §15.5 validation category.

## Definition of Done
- [ ] Project DoD is satisfied and negative-path evidence is linked.

## Evidence Required
- Focused configuration-test output, safe failing-command samples, Django check output, secret-leak inspection, Git diff.

## Risks / Notes
- Tests must not preserve synthetic secret values in snapshots or command logs unnecessarily.

## Blocking Conditions
Stop for a requirement/design conflict over required/default behavior, unsafe diagnostic demand, or validation that requires unrelated modules.
