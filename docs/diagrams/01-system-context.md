# 01 — NEXETL System Context

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show NEXETL at the highest governed system-context level.

## Scope

Platform

## Governed Sources

- NEXETL-DOC-001 / Approved
- NEXETL-DOC-004 / Approved
- NEXETL-DOC-009 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    HU["Human Users"] --> VI["Visual Interaction Boundary"]
    PC["Programmatic / Automation Clients"] --> API["Programmatic API Boundary"]
    VI --> NX["NEXETL Platform"]
    API --> NX
    DEV["Connector / Plugin Developers"] --> EB["Governed Extension Boundary"]
    EB <--> NX
    EB <--> ES["External Source / Target Systems"]
    NX --> OPS["Operational / Observability Systems<br/>where configured"]
    INF["Deployment / Infrastructure Environment"] --- NX
    SEC["External Identity / Security Services<br/>where later approved"] -. future .-> NX
~~~

## Interpretation Notes

- The external-system node is conceptual and names no vendor.
- Visual and programmatic interaction converge on the same governed platform semantics.
- The extension boundary mediates technology-specific external interaction.

## Unresolved / Deferred Boundaries

- External identity/security-service integration remains subject to later approval.
- Production deployment topology and named operational products remain unresolved.
