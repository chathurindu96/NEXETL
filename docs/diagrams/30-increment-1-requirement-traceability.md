# 30 — Increment 1 Requirement Traceability

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Visualize the approved delivery mappings for the three core Increment 1 requirements.

## Scope

Increment 1

## Governed Sources

- NEXETL-REG-002 v1.1 / Approved
- NEXETL-DES-001 v1.0 / Approved
- NEXETL-PLAN-001 v0.1 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    subgraph R1["NEXETL-REQ-001 — Create Pipeline Definition"]
        R1Req["Requirement"] --> R1Domain["PipelineDefinition<br/>Register use case"]
        R1Domain --> R1Api["POST /api/pipeline-definitions/"]
        R1Api --> R1Persist["INSERT id<br/>PostgreSQL"]
        R1Persist --> R1Front["/pipelines/new"]
        R1Front --> R1Security["Authentication + register capability"]
        R1Security --> R1Tests["Unit + integration + API + UI + E2E"]
        R1Tests --> R1Wp["WP-05, WP-06, WP-08, WP-10, WP-13, WP-17"]
    end
    subgraph R2["NEXETL-REQ-002 — Inspect Pipeline Definition"]
        R2Req["Requirement"] --> R2Domain["PipelineDefinition<br/>Inspect use case"]
        R2Domain --> R2Api["GET /api/pipeline-definitions/{id}/"]
        R2Api --> R2Persist["Primary-key lookup<br/>PostgreSQL"]
        R2Persist --> R2Front["/pipelines/[pipelineDefinitionId]"]
        R2Front --> R2Security["Authentication + inspect capability"]
        R2Security --> R2Tests["Unit + integration + API + UI + E2E"]
        R2Tests --> R2Wp["WP-05, WP-06, WP-08, WP-10, WP-14, WP-17"]
    end
    subgraph R4["NEXETL-REQ-004 — Retain Pipeline Definition"]
        R4Req["Requirement"] --> R4Domain["Retained identity<br/>persistence coordination"]
        R4Domain --> R4Api["Committed 201 + subsequent GET"]
        R4Api --> R4Persist["Durable PostgreSQL row"]
        R4Persist --> R4Front["Reload remains inspectable"]
        R4Front --> R4Security["Database access boundary"]
        R4Security --> R4Tests["Migration + integration + E2E retention"]
        R4Tests --> R4Wp["WP-04, WP-06, WP-14, WP-17"]
    end
~~~

## Interpretation Notes

- The three chains reproduce the explicit DES-001 design mappings and PLAN-001 responsible work packages.
- Each arrow is a traceability progression, not a claim that one architectural layer executes the next in that visual order.
- REG-002 remains the governed requirement-to-domain-to-architecture register.

## Unresolved / Deferred Boundaries

- This diagram does not add mappings for requirements lacking explicit current evidence.
- Broader platform traceability and future-increment implementation mappings remain governed work.
