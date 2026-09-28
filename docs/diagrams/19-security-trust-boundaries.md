# 19 — Security Trust Boundaries

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the governed trust boundaries crossed by browser input, protected application behavior, persistence, and diagnostics.

## Scope

Both

## Governed Sources

- NEXETL-DOC-010 / Approved
- NEXETL-ADR-004 / Accepted
- NEXETL-ADR-005 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    U["Untrusted Browser Input"]
    subgraph BrowserBoundary["Browser / SvelteKit Boundary"]
      FE["SvelteKit UI + API Client"]
    end
    subgraph ServerBoundary["Django / DRF Trust Boundary"]
      SC["Session + CSRF Boundary"]
      AZ["Authorization Boundary"]
      APP["Application / Domain"]
      SAFE["Sanitized Response Boundary"]
    end
    DB[("PostgreSQL<br/>Protected Persistence")]
    DIAG["Protected Diagnostics"]
    U --> FE
    FE -->|HTTP + cookie + input| SC
    SC --> AZ --> APP --> DB
    APP --> SAFE --> FE
    APP --> DIAG
    SC --> DIAG
    AZ --> DIAG
~~~

## Interpretation Notes

- Browser input remains untrusted across the HTTP boundary.
- Session/CSRF and authorization are distinct controls before protected behavior.
- Diagnostics are protected and separated from sanitized client responses.

## Unresolved / Deferred Boundaries

- Production network/TLS/ingress topology and external identity integration remain deferred.
- The diagram does not imply a separate security microservice.
