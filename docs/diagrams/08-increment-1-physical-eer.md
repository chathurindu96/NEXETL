# 08 — Increment 1 Physical EER

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Represent the concrete DES-001 PostgreSQL persistence design without speculative schema.

## Scope

Increment 1

## Governed Sources

- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
erDiagram
    nexetl_pipeline_definition {
        uuid id PK
    }
~~~

## Interpretation Notes

- The physical table name is nexetl_pipeline_definition.
- The table contains one non-null UUID primary-key column: id.
- The intentionally small diagram is the complete Increment 1 physical domain schema.

## Unresolved / Deferred Boundaries

- No name, status, timestamps, owner, tenant, revision, metadata, soft-delete field, secondary index, or future table is implied.
- Django framework-owned tables are outside this domain EER.
