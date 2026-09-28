# 31 — NEXETL Platform-Wide Conceptual EER / Data Model

> Derived visualization only. Governed source documents remain authoritative.

> **Platform-wide conceptual model. Physical persistence for future increments remains subject to later Detailed Design.**

## Purpose

Provide the broadest conservative entity-relationship view supported by the current governed platform baseline.

## Scope

Platform

## Governed Sources

- NEXETL-DOC-008 / Approved
- NEXETL-DOC-011 / Approved
- NEXETL-DOC-012 / Approved
- NEXETL-DOC-013 / Approved
- NEXETL-DOC-014 / Approved
- NEXETL-DOC-015 / Approved

## Mermaid Diagram

~~~mermaid
erDiagram
    PIPELINE ||--o{ PIPELINE_EXECUTION : "is executed as"
    EXTERNAL_SYSTEM ||--o{ INTEGRATION_CONFIGURATION : "is described by"
    CONNECTOR_PLUGIN_CAPABILITY ||--o{ INTEGRATION_CONFIGURATION : "supports"
    PIPELINE ||--o{ AUTOMATED_INITIATION_CONFIGURATION : "may be targeted by"
    PIPELINE_EXECUTION ||--o{ OPERATIONAL_RECORD : "is described by"
~~~

## Interpretation Notes

- This is a conceptual EER, not a physical PostgreSQL schema.
- The entities and conservative cardinalities shown are limited to relationships supported strongly enough by DOC-008 and the applicable architecture documents.
- Approved concepts whose relationships or cardinalities remain unresolved are intentionally absent rather than guessed.
- Diagram 08 remains the concrete Increment 1 physical EER and is not expanded by this platform view.

## Unresolved / Deferred Boundaries

- Pipeline versus Pipeline Definition, revisions, Step/Node/Task terminology and Pipeline lifecycle vocabulary remain unresolved where identified by the baseline.
- Physical tables, columns, keys and persistence for executions, initiation, operational records, connectors, extensions, protected credentials and audit concepts remain subject to later Detailed Design.
- Connector runtime, extension runtime, execution-engine internals, ownership, tenancy, RBAC and sharing are not established by this diagram.
