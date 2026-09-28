# 15 — Increment 1 REST API Resource Map

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Map only the three approved Increment 1 REST operations to their governed responsibilities and representations.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-017 / Approved
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    POST["POST<br/>/api/pipeline-definitions/"]
    GET["GET<br/>/api/pipeline-definitions/{pipelineDefinitionId}/"]
    CSRF["GET<br/>/api/security/csrf/"]
    REG["RegisterPipelineDefinition"]
    INS["InspectPipelineDefinition"]
    BOOT["CSRF Bootstrap"]
    RES["PipelineDefinitionResult<br/>id only"]
    CREATED["201 + Location + id"]
    OK["200 + id"]
    EMPTY["204 No Content"]
    POST --> REG --> RES --> CREATED
    GET --> INS --> RES --> OK
    CSRF --> BOOT --> EMPTY
~~~

## Interpretation Notes

- Registration accepts no client-controlled domain fields.
- Inspection uses the path UUID and returns the same minimal representation.
- The CSRF endpoint bootstraps browser protection and creates no Pipeline Definition.

## Unresolved / Deferred Boundaries

- No list, update, delete, search, filter, sort, pagination, or execution endpoint is approved for Increment 1.
- Platform-wide API versioning remains deferred.
