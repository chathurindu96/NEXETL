# 16 — External Error Translation Flow

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show how internal failures become stable, sanitized external errors.

## Scope

Both

## Governed Sources

- NEXETL-DOC-020 / Approved
- NEXETL-ADR-007 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    FAIL["Domain / Application / Framework / Dependency Failure"]
    CLASS["Semantic Classification"]
    CENTRAL["Centralized Error Translation"]
    SAFE["Sanitization"]
    CODE["Stable NEXETL Error Code"]
    STATUS["HTTP Status"]
    MSG["Safe Message"]
    DETAILS["Optional Structured Details"]
    CORR["Optional Correlation Reference"]
    FE["Frontend Error Handling"]
    FAIL --> CLASS --> CENTRAL --> SAFE
    SAFE --> CODE --> FE
    SAFE --> STATUS --> FE
    SAFE --> MSG --> FE
    SAFE --> DETAILS --> FE
    SAFE --> CORR --> FE
~~~

## Interpretation Notes

- External error behavior is semantic and centrally translated.
- Internal exception, framework, SQL, and secret details remain outside the client response.
- Optional details and correlation references appear only where governed and safe.

## Unresolved / Deferred Boundaries

- A platform-wide correlation architecture and complete future error-code catalogue remain unresolved.
- Problem Details is not mandated by the current decision.
