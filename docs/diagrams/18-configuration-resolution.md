# 18 — Configuration Resolution

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show ADR-006 concern-owned configuration resolution, validation, and protected secret inputs.

## Scope

Both

## Governed Sources

- NEXETL-DOC-020 / Approved
- NEXETL-ADR-006 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    DEF["Safe Documented Default<br/>where allowed"]
    ENV["Explicit Environment / Deployment Value"]
    SECRET["Protected Secret Input<br/>no fallback"]
    OWN["Concern-Owned Central Resolver"]
    VALID["Type + Semantic Validation"]
    APP["Validated Application Configuration"]
    FAIL["Fail Startup Safely"]
    DEF --> OWN
    ENV --> OWN
    SECRET --> OWN
    OWN --> VALID
    VALID -->|Valid| APP
    VALID -->|Missing / Invalid| FAIL
~~~

## Interpretation Notes

- Each configuration concern has one semantic owner.
- Safe defaults exist only where explicitly allowed; secrets have no usable fallback.
- Validation occurs before backend readiness.

## Unresolved / Deferred Boundaries

- ADR-006 does not establish one universal precedence hierarchy for every concern.
- Production secret-manager selection and wider deployment-source mechanics remain deferred.
