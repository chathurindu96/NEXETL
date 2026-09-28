# 04 — Backend Module Dependency

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Reproduce the approved Increment 1 backend module dependency direction.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-016 / Approved
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart TB
    ROOT["nexetl Django bootstrap/composition"]
    API["pipelines.api<br/>DRF adapter"]
    APP["pipelines.application<br/>use cases + ports"]
    DOM["pipelines.domain<br/>PipelineDefinition + ID"]
    INF["pipelines.infrastructure<br/>persistence + authorization adapters"]
    ORM["Django ORM"]
    PG[("PostgreSQL")]
    SEC["Django session/auth permission facilities"]
    ROOT --> API
    ROOT --> INF
    API --> APP
    APP --> DOM
    INF --> APP
    INF --> DOM
    INF --> ORM
    ORM --> PG
    INF --> SEC
~~~

## Interpretation Notes

- Semantics are reused directly from DES-001.
- Domain and application responsibilities do not depend on DRF or ORM adapters.
- Composition owns wiring between inward-facing responsibilities and infrastructure.

## Unresolved / Deferred Boundaries

- No additional Django applications or backend modules are implied.
- WP-02 remains not started.
