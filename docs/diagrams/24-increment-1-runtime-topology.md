# 24 — Increment 1 Runtime Topology

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Separate the runtime topology authorized for Increment 1 from future platform runtime capabilities.

## Scope

Both

## Governed Sources

- NEXETL-DOC-009 / Approved
- NEXETL-DOC-019 / Approved
- NEXETL-DOC-027 / Approved
- NEXETL-DES-001 v1.0 / Approved
- NEXETL-PLAN-001 v0.1 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    subgraph Current["Current Increment 1"]
        Browser["Browser"] --> Frontend["SvelteKit frontend"]
        Frontend -->|REST| Backend["Django / DRF modular monolith"]
        Backend --> Metadata["PostgreSQL metadata store"]
    end
    subgraph Future["Future platform runtime capabilities — not Increment 1"]
        Runtime["Long-running execution runtime"]
        Initiation["Automated initiation / scheduling capability"]
        Extensions["Connector and extension runtime capability"]
    end
    Backend -. "future governed integration" .-> Runtime
    Initiation -. "future initiation" .-> Runtime
    Runtime -. "future capability use" .-> Extensions
~~~

## Interpretation Notes

- Increment 1 is the browser, SvelteKit, Django/DRF and PostgreSQL slice for Pipeline Definition registration, inspection and retention.
- Future boxes are approved conceptual runtime capabilities only; they are not part of the Increment 1 implementation topology.
- The diagram preserves modular-monolith semantics and does not imply separate deployment of logical backend modules.

## Unresolved / Deferred Boundaries

- Production hosting, scaling, network and infrastructure-provider choices remain unresolved where not approved.
- Runtime, scheduling, connector and extension implementation technologies are not selected by this diagram.
