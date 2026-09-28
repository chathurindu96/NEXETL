# NEX-108 — Configure Increment 1 Security Bootstrap Settings

## Metadata
- Type: TASK
- Epic / Parent WP: WP-03 — Configuration and Startup Validation
- Sprint: Sprint 1 candidate
- Priority: P1
- Story Points: 3
- Component: Security
- Status: Candidate for commitment
- Dependencies: NEX-105, NEX-106

## User / Engineering Value
Secure, explicit bootstrap policy avoids accidentally weakening session or CSRF controls before their later behavioral integration.

## Background
DES-001 defines secret key, debug, allowed hosts, and secure-cookie settings. Local HTTP requires explicit Secure-flag overrides; debug must never infer them. WP-07 owns authentication/session/CSRF behavior.

## Problem Statement
Security-relevant Django bootstrap settings must be centrally mapped and validated without implementing later security flows.

## Scope
- Configure secret key, debug, allowed hosts, session-cookie secure, and CSRF-cookie secure policy values.
- Preserve secure defaults and explicit local HTTP overrides.
- Set fixed safe cookie attributes already required by DES-001 where they are configuration policy.

## Out of Scope
- Login, principal establishment, session lifecycle behavior, CSRF bootstrap endpoint, CSRF request enforcement tests, authorization, and frontend credentials handling.

## Governed Sources
- PLAN-001 §9, WP-03; WP-07 boundary in §13.
- DES-001 §§13.1–13.5, 15.1–15.5, 20.7, 21.1–21.2, 21.8.
- ADR-004 and ADR-006; DOC-010 and DOC-020.

## Requirements Traceability
- NEXETL-REQ-092 — Authentication Required for Protected Access.
- NEXETL-REQ-095 — Secret Confidentiality.
- NEXETL-REQ-098 — Fail-Safe Security Behavior.
- NEXETL-REQ-113 — Controlled Configuration.

## Technical Design Constraints
- Session credential remains HttpOnly; SameSite policy follows DES-001.
- Secure flags default true and are explicitly false only for local HTTP.
- DEBUG does not control security flags.
- This ticket configures policy only and must not claim WP-07 completion.

## Implementation Tasks
- [ ] Reconcile existing security-setting names and defaults with DES-001.
- [ ] Wire validated values into Django settings.
- [ ] Add configuration-level tests for secure defaults and explicit local overrides.
- [ ] Assert debug/security independence.
- [ ] Confirm no endpoint, middleware bypass, or auth flow is introduced.

## Files / Areas Expected to Change
- Human-maintained: `backend/src/nexetl/configuration.py`, `backend/src/nexetl/settings.py`, configuration tests, safe example/docs.
- Generated: none expected.

Before modifying code, perform an impact assessment. Keep the change in its owning boundary. If it unexpectedly requires manual changes across many unrelated files, **STOP** and report the large blast radius, duplicated knowledge, leaking boundaries, and whether the cause is implementation debt, DES ambiguity, or architecture contradiction. Do not perform shotgun surgery to make tests pass; report generated and human-maintained files separately.

## Installation Impact
- Packages expected: none.
- Installation commands: none.
- `INSTALLATION.md`: update only for environment setup changes.

## Runtime Command Impact
- `RUN.md` must document explicit local HTTP overrides and warn that they are not production defaults.

## Database Impact
- None; database-backed session behavior belongs to WP-07/WP-04 prerequisites.

## Security Considerations
- This ticket is security-sensitive: fail closed, redact secrets, retain HttpOnly, avoid permissive hosts, and never disable CSRF for convenience.

## Error / Failure Considerations
- Missing secret, placeholder secret, invalid boolean, or empty host list fails safely before readiness.

## Test Requirements
- Configuration/security tests for defaults, explicit overrides, debug independence, host parsing, secret redaction, and Django settings mapping.

## Documentation Requirements
- Update `RUN.md`, `INSTALLATION.md` if applicable, `COMMAND-LOG.md`, and security/configuration traceability.

## Acceptance Criteria
- [ ] Secure-cookie defaults are true and require explicit local HTTP override.
- [ ] Session cookie is configured HttpOnly and the approved SameSite policy is represented.
- [ ] DEBUG cannot silently weaken cookie/CSRF settings.
- [ ] No WP-07 authentication/session/CSRF behavior is implemented or claimed.

## Definition of Done
- [ ] Project DoD is satisfied and security-focused configuration evidence is linked.

## Evidence Required
- Configuration/security test output, redacted resolved-setting evidence, Django system check, focused diff.

## Risks / Notes
- Local browser testing can fail if Secure flags remain true over HTTP; the remedy is an explicit local override, not coupling to DEBUG.

## Blocking Conditions
Stop for a request to disable a security control, infer security from debug, expose secrets, or implement WP-07 behavior.
