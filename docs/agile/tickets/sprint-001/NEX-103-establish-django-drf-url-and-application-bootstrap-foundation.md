# NEX-103 — Establish Django/DRF URL and Application Bootstrap Foundation

## Metadata
- Type: TASK
- Epic / Parent WP: WP-02 — Backend/Django Bootstrap Foundation
- Sprint: Sprint 1 candidate
- Priority: P1
- Story Points: 3
- Component: API
- Status: Candidate for commitment
- Dependencies: NEX-101; NEX-102 where package registration is required

## User / Engineering Value
A minimal URL and DRF bootstrap creates a controlled future API composition point without inventing product operations.

## Background
PLAN-001 requires Django settings integration, URL composition, and DRF foundation. DES-001 reserves central API/error and CSRF composition points while deferring their behavior to later WPs.

## Problem Statement
The backend needs a verifiable HTTP/DRF composition shell, but Sprint 1 must not expose Pipeline Definition or security behavior.

## Scope
- Configure DRF as an installed framework dependency.
- Establish the root URL configuration and empty/narrow application composition point.
- Verify Django resolves the URL configuration without business routes.

## Out of Scope
- Pipeline endpoints, CSRF endpoint behavior, serializers, views, OpenAPI completion, authentication/authorization, and external error translation.

## Governed Sources
- PLAN-001 §8, WP-02.
- DES-001 §§6.1–6.3, 7.1–7.2, 11.5, 12.6.
- ADR-001, ADR-007; DOC-016, DOC-017, DOC-023.

## Requirements Traceability
- NEXETL-REQ-112 — Explicit Responsibility Boundaries.
- NEXETL-REQ-114 — Governed Change Traceability.
- NEXETL-REQ-120 — Environment-Specific Dependency Governance.

## Technical Design Constraints
- Root routing is composition, not domain logic.
- Do not create unapproved endpoints, placeholder success responses, or an error catalogue.
- Preserve central translation and CSRF extension points without implementing WP-07/WP-09.

## Implementation Tasks
- [ ] Assess existing settings and URL composition.
- [ ] Add only missing DRF/bootstrap configuration.
- [ ] Verify URL resolution and system checks.
- [ ] Confirm no business endpoint is reachable.
- [ ] Review imports and scope.

## Files / Areas Expected to Change
- Human-maintained: `backend/src/nexetl/settings.py`, `backend/src/nexetl/urls.py`, minimal application registration metadata if required.
- Generated: none expected.

Before modifying code, perform an impact assessment. Keep the change in its owning boundary. If it unexpectedly requires manual changes across many unrelated files, **STOP** and report the large blast radius, duplicated knowledge, leaking boundaries, and whether the cause is implementation debt, DES ambiguity, or architecture contradiction. Do not perform shotgun surgery to make tests pass; report generated and human-maintained files separately.

## Installation Impact
- Packages expected: DRF only if absent from governed lock state.
- Installation commands: governed uv command only if required.
- `INSTALLATION.md`: update only for an actual dependency change.

## Runtime Command Impact
- `RUN.md` should retain the validated Django system-check/start commands.

## Database Impact
- None.

## Security Considerations
- Do not disable security middleware or install permissive defaults to simplify bootstrap.

## Error / Failure Considerations
- Invalid routing/configuration must fail through normal Django startup checks; no raw secret output.

## Test Requirements
- Django system check, root URL import/resolution test, and negative assertion that no Pipeline Definition business routes exist.

## Documentation Requirements
- Update `COMMAND-LOG.md` and implementation traceability; update install/run documentation only when behavior changes.

## Acceptance Criteria
- [ ] Django and DRF initialize with valid controlled configuration.
- [ ] Root URL configuration resolves without exposing WP-07+ or WP-10 routes.
- [ ] No business serializer, view, route, or error contract is implemented.

## Definition of Done
- [ ] Project DoD is satisfied with bootstrap and negative-scope evidence.

## Evidence Required
- System-check/test output, URL inventory, focused Git diff, dependency-lock evidence if changed.

## Risks / Notes
- Reserved extension points must not become speculative implementations.

## Blocking Conditions
Stop for an unapproved API behavior, architecture contradiction, hidden security bypass, or broad unrelated edits.
