# 02 — Platform Container Architecture

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the approved Increment 1 application containers and clearly separate future platform runtime responsibilities.

## Scope

Both

## Governed Sources

- NEXETL-DOC-009 / Approved
- NEXETL-DOC-027 / Approved
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    subgraph Current["Current Increment 1"]
      B["Browser"]
      FE["SvelteKit Frontend"]
      BE["Django / DRF Backend"]
      DB[("PostgreSQL<br/>Platform Metadata")]
      B --> FE
      FE -->|REST /api| BE
      BE --> DB
    end
    subgraph Future["Future / not Increment 1"]
      RT["Runtime Responsibilities"]
      XB["Extension / Connector Boundary"]
      ES["External Systems"]
      RT --> XB
      XB <--> ES
    end
    BE -. governed future integration .-> RT
~~~

## Interpretation Notes

- The current boxes are application/runtime containers, not microservices.
- Increment 1 uses the browser, SvelteKit, Django/DRF, and PostgreSQL path.
- Future runtime responsibilities are shown only as approved logical direction.

## Unresolved / Deferred Boundaries

- Production container orchestration, worker topology, scheduler, broker, and execution-engine internals remain unresolved.
- Future boxes are not authorized Increment 1 implementation.
