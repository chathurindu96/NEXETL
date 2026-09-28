# 11 — Inspect Pipeline Definition Sequence

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Faithfully reproduce the approved DES-001 inspection interaction.

## Scope

Increment 1

## Governed Sources

- NEXETL-ADR-004 / Accepted
- NEXETL-ADR-005 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
sequenceDiagram
    actor User
    participant UI as SvelteKit UI
    participant API as DRF API
    participant Auth as Session Authentication
    participant App as Inspect Use Case
    participant Az as Authorization Gateway
    participant Store as PipelineDefinitionStore
    participant DB as PostgreSQL
    User->>UI: Open Pipeline Definition
    UI->>API: GET /api/pipeline-definitions/{id}/ + session cookie
    API->>Auth: authenticate
    Auth-->>API: authenticated principal
    API->>API: validate UUID path
    API->>App: inspect(principal, id)
    App->>Az: require pipeline_definition.inspect before lookup
    Az-->>App: allowed
    App->>Store: get(id)
    Store->>DB: SELECT by primary key
    DB-->>Store: row or no row
    Store-->>App: entity or not found
    App-->>API: result or semantic not-found
    API-->>UI: 200 representation or governed error
    UI-->>User: inspection or safe failure state
~~~

## Interpretation Notes

- The inspect capability is checked before any protected persistence lookup.
- Only an authorized missing record becomes the governed not-found outcome.
- The returned representation contains the Pipeline Definition ID only.

## Unresolved / Deferred Boundaries

- Identifier knowledge never grants authorization.
- List, search, update, delete, ownership, and revision behavior are outside Increment 1.
