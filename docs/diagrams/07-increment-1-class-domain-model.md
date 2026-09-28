# 07 — Increment 1 UML Class / Domain Model

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show only the approved Increment 1 Pipeline Definition domain and application concepts.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-008 / Approved
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
classDiagram
    class PipelineDefinition {
      +id: PipelineDefinitionId
    }
    class PipelineDefinitionId {
      +value: UUID
    }
    class RegisterPipelineDefinition {
      +execute(principal) PipelineDefinitionResult
    }
    class InspectPipelineDefinition {
      +execute(principal, id) PipelineDefinitionResult
    }
    class PipelineDefinitionStore {
      <<port>>
      +create(definition)
      +get(id)
    }
    PipelineDefinition *-- PipelineDefinitionId
    RegisterPipelineDefinition ..> PipelineDefinition
    RegisterPipelineDefinition ..> PipelineDefinitionStore
    InspectPipelineDefinition ..> PipelineDefinitionStore
    PipelineDefinitionStore ..> PipelineDefinition
~~~

## Interpretation Notes

- PipelineDefinition contains exactly its immutable identity in Increment 1.
- The use cases depend on the focused store port rather than a framework persistence model.
- UUID v4 identity is generated server-side during registration.

## Unresolved / Deferred Boundaries

- Pipeline versus Pipeline Definition formal terminology remains UL-001.
- Revision, lifecycle, ownership, tenancy, execution, and structural element concepts are not part of this Increment 1 model.
