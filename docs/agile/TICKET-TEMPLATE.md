# NEX-### — Title

## Metadata

- Type: STORY | TASK | BUG | SPIKE
- Epic / Parent WP: WP-## — exact PLAN-001 title
- Sprint: Unscheduled / Backlog or approved iteration
- Priority: P0 | P1 | P2 | P3
- Story Points: 1 | 2 | 3 | 5 | 8
- Component:
- Status: Backlog | Ready | Candidate for commitment | In Progress | In Review | Blocked | Done
- Dependencies:

## User / Engineering Value

Why this work matters.

## Background

Governed context and current evidence.

## Problem Statement

The bounded problem to solve.

## Scope

- Included behavior or deliverables.

## Out of Scope

- Explicit exclusions.

## Governed Sources

- Exact PLAN-001 WP section.
- Exact DES-001 sections.
- Applicable Accepted ADRs and engineering standards.

## Requirements Traceability

- Real NEXETL requirement identifiers verified in REG-002.

## Technical Design Constraints

- Binding architecture and design constraints.

## Implementation Tasks

- [ ] Perform a pre-change impact assessment.
- [ ] Add concrete, reviewable work items.
- [ ] Verify the bounded result.

## Files / Areas Expected to Change

- Expected owning files/directories.
- Report generated files separately from human-maintained files.

Before modifying code, perform an impact assessment. A routine localized change should remain inside its owning boundary where practical. If a seemingly small ticket unexpectedly requires manual modification across many unrelated modules or files, **STOP** and report why the blast radius is large, whether knowledge is duplicated, whether boundaries are leaking, and whether the cause is implementation debt, DES ambiguity, or an architecture contradiction. Do not perform shotgun surgery simply to make tests pass.

## Installation Impact

- Packages expected:
- Installation commands:
- `INSTALLATION.md` update required / not required:

## Runtime Command Impact

- `RUN.md` update required / not required and why.

## Database Impact

- None | configuration only | migration | query | schema change.
- Any SQL/query introduced must be documented in `DATABASE.md`.

## Security Considerations

- Authentication, authorization, CSRF, secrets, validation, error leakage, and DB safety as applicable.

## Error / Failure Considerations

- Expected safe failure behavior.

## Test Requirements

- Applicable unit, application, integration, API, security, configuration, frontend, and E2E checks.

## Documentation Requirements

- Applicable updates to `INSTALLATION.md`, `RUN.md`, `DATABASE.md`, `COMMAND-LOG.md`, and implementation traceability.

## Acceptance Criteria

- [ ] Objective, testable criteria; use Given / When / Then where useful.

## Definition of Done

- [ ] Project Definition of Done satisfied where applicable.
- [ ] Ticket-specific completion conditions satisfied.

## Evidence Required

- Tests, command output, focused Git diff, system/configuration checks, or screenshots where appropriate.

## Risks / Notes

- Known risks, assumptions, and refinement notes.

## Blocking Conditions

Stop implementation for a material requirement, Accepted ADR, architecture, DES, or PLAN contradiction; an unresolved architecture-significant choice; missing authorization; or an unexpected cross-boundary blast radius that cannot be explained and reviewed safely.
