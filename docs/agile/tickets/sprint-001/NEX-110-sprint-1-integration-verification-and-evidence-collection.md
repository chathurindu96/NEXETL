# NEX-110 — Sprint 1 Integration Verification and Evidence Collection

## Metadata
- Type: TASK
- Epic / Parent WP: WP-02 / WP-03
- Sprint: Sprint 1 candidate
- Priority: P1
- Story Points: 3
- Component: Testing
- Status: Candidate for commitment
- Dependencies: Candidate commitment and completion of selected NEX-101 through NEX-109 work

## User / Engineering Value
An integrated evidence review proves that the Sprint Goal is met and prevents partial checks or accidental scope expansion from being mistaken for completion.

## Background
PLAN-001 requires objective verification and DES-001 defines bootstrap, configuration, dependency, and security-control checks. A successful process exit alone is insufficient.

## Problem Statement
Individual ticket evidence must converge into a repeatable Sprint-level result that proves WP-02/WP-03 outcomes and absence of WP-04+ implementation.

## Scope
- Verify Django boots and system checks pass under valid configuration.
- Verify valid, missing, and invalid configuration paths and secret-safe failures.
- Verify dependency direction and documentation completeness.
- Audit repository scope for accidental WP-04+ implementation.
- Assemble review evidence and unresolved blockers.

## Out of Scope
- Fixing newly discovered defects without ticketing/impact review, database connectivity as WP-04 completion, migrations, Pipeline behavior, APIs, auth/authz behavior, and frontend work.

## Governed Sources
- PLAN-001 §§8–9, 25–26.
- DES-001 §§6–7, 15, 19.1–19.6, 19.11, 21.8, 25, 27–28.
- DOC-023, DOC-024, DOC-025.

## Requirements Traceability
- NEXETL-REQ-095 — Secret Confidentiality.
- NEXETL-REQ-112 — Explicit Responsibility Boundaries.
- NEXETL-REQ-113 — Controlled Configuration.
- NEXETL-REQ-114 — Governed Change Traceability.
- NEXETL-REQ-115 — Independent Core Behavior Verification.
- NEXETL-REQ-117 — Deterministic Testability.
- NEXETL-REQ-118 — Verification Mapping.
- NEXETL-REQ-119 — Containerized Deployment Portability.
- NEXETL-REQ-120 — Environment-Specific Dependency Governance.

## Technical Design Constraints
- Verification must use documented commands and controlled, synthetic values.
- Keep PostgreSQL optional to this Sprint’s WP-03 configuration checks; do not claim WP-04.
- Negative scope verification is mandatory.

## Implementation Tasks
- [ ] Confirm committed tickets meet acceptance criteria and project DoD.
- [ ] Reproduce clean dependency/lock checks where environment permits.
- [ ] Run focused and full backend tests plus Django system check.
- [ ] Exercise startup configuration failure matrix and review output for leakage.
- [ ] Audit imports, routes, models, migrations, and frontend changes for forbidden scope.
- [ ] Review mandatory documentation and traceability.
- [ ] Prepare Sprint Review evidence and record blockers honestly.

## Files / Areas Expected to Change
- Human-maintained: evidence/traceability documentation only; defects require their owning ticket or a new BUG.
- Generated: test/cache artifacts only; keep ignored and report separately.

Before modifying code, perform an impact assessment. Keep the change in its owning boundary. If it unexpectedly requires manual changes across many unrelated files, **STOP** and report the large blast radius, duplicated knowledge, leaking boundaries, and whether the cause is implementation debt, DES ambiguity, or architecture contradiction. Do not perform shotgun surgery to make tests pass; report generated and human-maintained files separately.

## Installation Impact
- Packages expected: none.
- Installation commands: no new installs; locked synchronization/check commands may run.
- `INSTALLATION.md`: update only if verification finds a factual gap.

## Runtime Command Impact
- `RUN.md` must contain every command used for repeatable Sprint-level verification.

## Database Impact
- Configuration only. No migration, query, schema change, or Pipeline table.

## Security Considerations
- Use synthetic secrets, redact evidence, inspect failure output, and verify no security bypass or permissive default entered scope.

## Error / Failure Considerations
- A failed criterion makes the relevant ticket incomplete or blocked; do not patch unrelated modules or relabel failure as environmental without evidence.

## Test Requirements
- Backend unit/configuration tests, Django check, dependency audit, secret-leak inspection, documentation completeness, and forbidden-scope audit.

## Documentation Requirements
- Verify all mandatory implementation documents and traceability; record commands and results in `COMMAND-LOG.md`.

## Acceptance Criteria
- [ ] Django boots/checks successfully with valid controlled configuration.
- [ ] Missing and invalid configuration fail deterministically without secret leakage.
- [ ] Dependency direction remains compliant and independently verifiable.
- [ ] Required documentation is complete and reproduces the verified workflow.
- [ ] No WP-04+ domain, persistence, migration, API business, auth/authz behavior, or frontend implementation entered scope.

## Definition of Done
- [ ] Project DoD is satisfied for every committed ticket and Sprint evidence is review-ready.
- [ ] Any incomplete criterion is visible as an open/blocked item rather than hidden follow-up.

## Evidence Required
- Test and system-check output, lock/sync check, configuration negative-path output, scope searches, documentation checklist, focused Git status/diff.

## Risks / Notes
- The 38-point candidate set is not a guaranteed commitment; verify only the final committed backlog while still auditing the Sprint Goal boundary.

## Blocking Conditions
Stop and report any material requirement/DES/architecture contradiction, unsafe evidence handling, unexplained broad change, or accidental entry into WP-04+ implementation.
