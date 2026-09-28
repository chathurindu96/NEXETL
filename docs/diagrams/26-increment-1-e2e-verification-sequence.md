# 26 — Increment 1 End-to-End Verification

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the critical end-to-end proof of registration, navigation, reload and PostgreSQL-backed retention.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-025 / Approved
- NEXETL-DES-001 v1.0 / Approved
- NEXETL-PLAN-001 v0.1 / Approved

## Mermaid Diagram

~~~mermaid
sequenceDiagram
    actor User as Authenticated User
    participant Browser
    participant UI as SvelteKit UI
    participant API as Django / DRF API
    participant DB as PostgreSQL
    User->>Browser: register Pipeline Definition
    Browser->>UI: submit registration
    UI->>API: POST /api/pipeline-definitions/
    API->>DB: persist server-generated ID
    DB-->>API: committed row
    API-->>UI: 201 Created + ID
    UI-->>Browser: navigate to /pipelines/[ID]
    Browser->>UI: load inspection route
    UI->>API: GET /api/pipeline-definitions/{ID}/
    API->>DB: select by ID
    DB-->>API: same retained ID
    API-->>UI: 200 + same ID
    User->>Browser: reload page
    Browser->>UI: reload inspection route
    UI->>API: GET /api/pipeline-definitions/{ID}/
    API->>DB: select by ID
    DB-->>API: same retained ID
    API-->>UI: 200 + same ID
    UI-->>User: retention proven
~~~

## Interpretation Notes

- The test proves that the same identifier remains retrievable after navigation and a full page reload.
- PostgreSQL-backed API retrieval, rather than browser-only state, is the evidence of retention.
- Authentication, CSRF and authorization controls remain applicable even where condensed in this verification sequence.

## Unresolved / Deferred Boundaries

- This sequence does not test Pipeline execution, transformation, connector behavior, deletion or long-term archival.
- Broader production reliability and disaster-recovery evidence remain outside Increment 1.
