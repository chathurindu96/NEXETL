# 13 — Authorization Decision Flow

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the backend-authoritative, capability-oriented authorization decision for Increment 1.

## Scope

Increment 1

## Governed Sources

- NEXETL-ADR-005 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart TD
    P["Authenticated Principal"]
    OP{"Requested Operation"}
    REG["Require<br/>pipeline_definition.register"]
    INS["Require<br/>pipeline_definition.inspect"]
    DEC{"Backend Authorization Decision"}
    ALLOW["Allow Use Case"]
    DENY["Deny Safely<br/>No Protected Effect / Lookup"]
    LOOK["Inspect Persistence Lookup"]
    EFFECT["Registration Persistence Effect"]
    P --> OP
    OP -->|Register| REG
    OP -->|Inspect| INS
    REG --> DEC
    INS --> DEC
    DEC -->|Known capability granted| ALLOW
    DEC -->|Missing / unknown / uncertain| DENY
    ALLOW -->|Register| EFFECT
    ALLOW -->|Inspect| LOOK
~~~

## Interpretation Notes

- Authorization is deny-by-default and backend authoritative.
- Register and inspect capabilities are independently enforced.
- Inspect authorization occurs before the protected resource lookup.

## Unresolved / Deferred Boundaries

- No roles, RBAC taxonomy, ownership, tenancy, sharing, or permission-administration model is introduced.
- Frontend authorization-aware states are non-authoritative.
