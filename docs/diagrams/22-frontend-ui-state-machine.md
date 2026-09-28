# 22 — Frontend UI State Machine

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the governed UI and request states for Increment 1 registration and inspection.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-018 / Approved
- NEXETL-ADR-003 / Accepted
- NEXETL-ADR-007 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
stateDiagram-v2
    [*] --> Ready
    Ready --> Submitting: submit registration
    Submitting --> Success: 201 Created
    Submitting --> ValidationError: validation response
    Submitting --> AuthenticationRequired: 401
    Submitting --> AuthorizationDenied: 403
    Submitting --> UnexpectedFailure: safe unexpected error
    Success --> Loading: navigate or reload inspection route
    Loading --> Success: inspected representation
    Loading --> AuthenticationRequired: 401
    Loading --> AuthorizationDenied: 403
    Loading --> NotAvailable: not visible / 404
    Loading --> UnexpectedFailure: safe unexpected error
    ValidationError --> Ready: correct input
    AuthenticationRequired --> Ready: authenticated return
    AuthorizationDenied --> Ready: leave denied state
    NotAvailable --> Ready: return to registration
    UnexpectedFailure --> Ready: retry or return
~~~

## Interpretation Notes

- These are frontend presentation and request states only.
- Success covers a successful registration result or a successfully loaded inspection representation according to the triggering transition.
- The frontend does not replace backend authentication, authorization, validation or error classification.

## Unresolved / Deferred Boundaries

- This is not a Pipeline lifecycle state diagram and establishes no Pipeline lifecycle vocabulary.
- Retry policy, session-expiry UX and a broader navigation model remain outside this Increment 1 view.
