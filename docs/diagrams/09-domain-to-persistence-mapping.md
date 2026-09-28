# 09 — Domain to Persistence Mapping

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the approved mapping from the Pipeline Definition domain concept through its persistence port and adapter to PostgreSQL.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-016 / Approved
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    D["PipelineDefinition"]
    P["PipelineDefinitionStore Port"]
    A["Django ORM Persistence Adapter"]
    T["nexetl_pipeline_definition"]
    DB[("PostgreSQL")]
    D --> P
    A --> P
    A --> T
    T --> DB
~~~

## Interpretation Notes

- The application interacts through PipelineDefinitionStore.
- The infrastructure adapter implements the port and maps the domain entity to the ORM record/table.
- PostgreSQL is the authoritative Increment 1 persistence mechanism.

## Unresolved / Deferred Boundaries

- No generic repository hierarchy or additional persistence technology is introduced.
- Physical evolution beyond the one approved table remains later design work.
