# 20 — Security Control Flow

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the ordered security controls around an Increment 1 application operation.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-010 / Approved
- NEXETL-DOC-023 / Approved
- NEXETL-ADR-004 / Accepted
- NEXETL-ADR-005 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    IN["Untrusted Input"]
    AUTHN["Authenticate"]
    CSRF["Enforce CSRF<br/>where relevant"]
    AUTHZ["Authorize Capability"]
    VALID["Validate Structure / Semantics"]
    MASS["Prevent Mass Assignment"]
    APP["Application / Domain"]
    PERSIST["Parameterized ORM Persistence"]
    SAFE["Sanitized Success / Error"]
    DIAG["Protected Diagnostic Handling"]
    IN --> AUTHN --> CSRF --> AUTHZ --> VALID --> MASS --> APP --> PERSIST --> SAFE
    AUTHN -. diagnostic context .-> DIAG
    CSRF -. diagnostic context .-> DIAG
    AUTHZ -. diagnostic context .-> DIAG
    VALID -. diagnostic context .-> DIAG
    APP -. diagnostic context .-> DIAG
~~~

## Interpretation Notes

- Controls fail safely and do not expose protected internals.
- No client-controlled Pipeline Definition field exists in the registration request.
- ORM persistence remains parameterized and behind the infrastructure boundary.

## Unresolved / Deferred Boundaries

- Full audit-event cataloguing, retention, and tamper-evidence policy remain unresolved.
- Production transport and secret-manager implementation remain later governed work.
