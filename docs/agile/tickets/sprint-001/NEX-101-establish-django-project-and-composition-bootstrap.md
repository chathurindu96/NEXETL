# NEX-101 — Establish Django Project and Composition Bootstrap

## Metadata
- Type: STORY
- Epic / Parent WP: WP-02 — Backend/Django Bootstrap Foundation
- Sprint: Sprint 1 candidate
- Priority: P1
- Story Points: 5
- Component: Backend
- Status: Candidate for commitment
- Dependencies: WP-01 complete; reconcile current backend foundation evidence before implementation

## User / Engineering Value
A stable composition root lets developers boot and verify the backend without coupling business rules to Django setup.

## Background
PLAN-001 requires a narrow `nexetl` Django bootstrap package. DES-001 assigns application-wide settings, URLs, ASGI/WSGI, and composition responsibilities to that shell. Repository evidence may already satisfy part of this ticket and must be assessed first.

## Problem Statement
The approved backend needs a minimal, reviewable Django project boundary that starts cleanly and creates no Pipeline Definition business behavior.

## Scope
- Establish or verify `manage.py` and the `nexetl` project/bootstrap package.
- Wire settings-module selection, ASGI, and WSGI entry points.
- Keep composition explicit and minimal.

## Out of Scope
- Pipeline Definition domain/application code, ORM models, migrations, business endpoints, authentication behavior, authorization behavior, error catalogue, and frontend work.

## Governed Sources
- PLAN-001 §8, WP-02.
- DES-001 §§6.1–6.3, 7.1–7.2, 20.
- ADR-001, ADR-002; DOC-016, DOC-023, DOC-024.

## Requirements Traceability
- NEXETL-REQ-112 — Explicit Responsibility Boundaries.
- NEXETL-REQ-114 — Governed Change Traceability.
- NEXETL-REQ-119 — Containerized Deployment Portability.
- NEXETL-REQ-120 — Environment-Specific Dependency Governance.

## Technical Design Constraints
- Use the approved Core Monorepo and uv boundary; no extra orchestrator.
- Keep `nexetl` a narrow composition/bootstrap package, not a business domain.
- Do not introduce hidden composition through Django signals.

## Implementation Tasks
- [ ] Assess current files and map satisfied, missing, or non-conforming outcomes.
- [ ] Confirm the narrow project package and entry points match DES-001.
- [ ] Add only missing bootstrap wiring.
- [ ] Run Django startup/system checks with controlled configuration.
- [ ] Review dependency direction and focused diff.

## Files / Areas Expected to Change
- Human-maintained: `backend/manage.py`, `backend/src/nexetl/`.
- Generated: none expected.

Before modifying code, perform an impact assessment. Keep the change in its owning boundary. If it unexpectedly requires manual changes across many unrelated files, **STOP** and report the large blast radius, duplicated knowledge, leaking boundaries, and whether the cause is implementation debt, DES ambiguity, or architecture contradiction. Do not perform shotgun surgery to make tests pass; report generated and human-maintained files separately.

## Installation Impact
- Packages expected: Django and Django REST Framework only if absent from the governed lock state.
- Installation commands: governed uv commands only.
- `INSTALLATION.md`: update only if installation state or commands change.

## Runtime Command Impact
- `RUN.md` must document verified backend check/start commands if missing or changed.

## Database Impact
- Configuration only at most; no query, migration, or schema change.

## Security Considerations
- No permissive security bypass; secrets remain external to source and command evidence.

## Error / Failure Considerations
- Missing or invalid bootstrap configuration must fail clearly without secret disclosure or raw internal state.

## Test Requirements
- Django system check and import/bootstrap smoke test; configuration supplied through controlled test inputs.

## Documentation Requirements
- Update `RUN.md`, `COMMAND-LOG.md`, and implementation traceability as applicable; update `INSTALLATION.md` only for dependency changes.

## Acceptance Criteria
- [ ] Given valid controlled configuration, when Django initializes, then the project loads and the system check reports no issues.
- [ ] The bootstrap package owns composition only and contains no Pipeline Definition business implementation.
- [ ] Current repository evidence is reused or verified rather than duplicated.

## Definition of Done
- [ ] Project DoD is satisfied and bootstrap evidence is linked.
- [ ] Focused review confirms WP-02 boundaries and no WP-03+ behavior was pulled in unnecessarily.

## Evidence Required
- System-check output, import/smoke-test output, focused Git diff, dependency review, documentation links.

## Risks / Notes
- Existing foundation files may make this a verification/repair ticket rather than net-new creation; Sprint Planning should adjust scope without retroactively claiming completion.

## Blocking Conditions
Stop for a material requirement/DES/architecture contradiction, an unapproved framework or topology choice, missing prerequisite, or unexplained cross-boundary blast radius.
