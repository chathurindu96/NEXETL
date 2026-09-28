# 21 — Frontend Navigation Flow

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the approved Increment 1 registration-to-inspection navigation and its governed response states.

## Scope

Increment 1

## Governed Sources

- NEXETL-ADR-003 / Accepted
- NEXETL-ADR-004 / Accepted
- NEXETL-ADR-007 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart TD
    Ready["Ready<br/>/pipelines/new"] --> Submit["Submit registration"]
    Submit --> Post["POST /api/pipeline-definitions/"]
    Post --> Created{"201 Created?"}
    Created -->|Yes| Navigate["Navigate with returned ID"]
    Navigate --> Route["/pipelines/[pipelineDefinitionId]"]
    Route --> Load["Load inspection view"]
    Load --> Inspect["GET /api/pipeline-definitions/{pipelineDefinitionId}/"]
    Inspect --> Success["Show inspected Pipeline Definition"]
    Created -->|Validation response| Validation["Show validation state"]
    Created -->|401| Authn["Authentication required"]
    Created -->|403| Authz["Authorization denied"]
    Created -->|Safe unexpected error| Failure["Show safe failure state"]
    Inspect -->|401| Authn
    Inspect -->|403| Authz
    Inspect -->|Not visible / 404| NotAvailable["Not available"]
    Inspect -->|Safe unexpected error| Failure
~~~

## Interpretation Notes

- The successful registration path uses the server-returned identifier to navigate to the inspection route.
- Inspection is loaded through the REST boundary; the route does not imply client-side persistence.
- Error states use the governed safe external contract.

## Unresolved / Deferred Boundaries

- Login and identity-management UX are outside Increment 1.
- List, update, delete, search, sharing, ownership and tenancy navigation are not defined here.
