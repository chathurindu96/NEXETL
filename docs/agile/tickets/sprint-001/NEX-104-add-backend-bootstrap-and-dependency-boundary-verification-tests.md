# NEX-104 — Add Backend Bootstrap and Dependency-Boundary Verification Tests

## Metadata
- Type: TASK
- Epic / Parent WP: WP-02 — Backend/Django Bootstrap Foundation
- Sprint: Sprint 1 candidate
- Priority: P1
- Story Points: 3
- Component: Testing
- Status: Candidate for commitment
- Dependencies: NEX-101, NEX-102, NEX-103

## User / Engineering Value
Repeatable checks prevent bootstrap regressions and framework dependencies from leaking into inner layers unnoticed.

## Background
PLAN-001 requires startup/system checks and practical dependency-direction tests. DES-001 selects pytest and pytest-django and requires independently testable inner behavior.

## Problem Statement
Manual inspection alone cannot reliably prove bootstrap readiness or preserve the approved dependency direction.

## Scope
- Test Django initialization and root URL bootstrap.
- Test/import-audit approved package direction using a maintainable, proportionate mechanism.
- Assert absence of prohibited Sprint 1 business implementation where practical.

## Out of Scope
- Domain/use-case, persistence, API behavior, auth/authz, frontend, and E2E tests.

## Governed Sources
- PLAN-001 §8, WP-02.
- DES-001 §§6.3–6.5, 19.1–19.2, 19.11.
- DOC-023 and DOC-025.

## Requirements Traceability
- NEXETL-REQ-114 — Governed Change Traceability.
- NEXETL-REQ-115 — Independent Core Behavior Verification.
- NEXETL-REQ-117 — Deterministic Testability.
- NEXETL-REQ-118 — Verification Mapping.

## Technical Design Constraints
- Tests must be deterministic and not require live PostgreSQL for bootstrap/package checks.
- Prefer explicit tests over brittle source-text assumptions; avoid a new architecture-significant analysis tool.

## Implementation Tasks
- [ ] Review existing tests and avoid duplicate coverage.
- [ ] Add bootstrap/system configuration tests.
- [ ] Add practical dependency-boundary verification.
- [ ] Add negative-scope assertion where stable and valuable.
- [ ] Run focused and complete backend test suites.

## Files / Areas Expected to Change
- Human-maintained: `backend/tests/` and test configuration in `backend/pyproject.toml` only if necessary.
- Generated: test caches only; they must remain ignored.

Before modifying code, perform an impact assessment. Keep the change in its owning boundary. If it unexpectedly requires manual changes across many unrelated files, **STOP** and report the large blast radius, duplicated knowledge, leaking boundaries, and whether the cause is implementation debt, DES ambiguity, or architecture contradiction. Do not perform shotgun surgery to make tests pass; report generated and human-maintained files separately.

## Installation Impact
- Packages expected: pytest and pytest-django only if absent from governed dev dependencies.
- Installation commands: governed `uv add --dev` only if required.
- `INSTALLATION.md`: update for an actual test dependency change.

## Runtime Command Impact
- `RUN.md` must include the repeatable backend test command if missing.

## Database Impact
- None; tests in this ticket must not require PostgreSQL or migrations.

## Security Considerations
- Test configuration uses synthetic values and must never emit or persist real secrets.

## Error / Failure Considerations
- Failures should identify the violated bootstrap or dependency rule without leaking configuration values.

## Test Requirements
- The ticket is test work: focused pytest, complete backend pytest, and Django system check must pass.

## Documentation Requirements
- Update test command/evidence in `RUN.md`, `COMMAND-LOG.md`, and traceability as applicable.

## Acceptance Criteria
- [ ] Tests fail when bootstrap cannot initialize under valid controlled inputs.
- [ ] A prohibited outward dependency from domain/application is detected by the selected check.
- [ ] Tests pass without PostgreSQL and without adding WP-05+ behavior.

## Definition of Done
- [ ] Project DoD is satisfied; tests are deterministic, readable, and included in normal backend verification.

## Evidence Required
- Focused/full pytest output, Django check output, deliberately validated failure behavior or review evidence, focused Git diff.

## Risks / Notes
- An overly clever dependency test can become maintenance debt; keep the mechanism transparent.

## Blocking Conditions
Stop if verification requires a new unapproved architecture tool, live external dependency, or invasive unrelated source changes.
