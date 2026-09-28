# 10 — Register Pipeline Definition Sequence

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Faithfully reproduce the approved DES-001 registration interaction.

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
    participant Auth as Session / CSRF
    participant App as Register Use Case
    participant Az as Authorization Gateway
    participant Store as PipelineDefinitionStore
    participant DB as PostgreSQL
    User->>UI: Register Pipeline Definition
    UI->>API: POST /api/pipeline-definitions/ + session cookie + CSRF header
    API->>Auth: authenticate + enforce CSRF
    Auth-->>API: authenticated principal
    API->>App: register(principal)
    App->>Az: require pipeline_definition.register
    Az-->>App: allowed
    App->>App: generate UUID and create domain entity
    App->>Store: create(entity) within transaction
    Store->>DB: INSERT id
    DB-->>Store: committed
    Store-->>App: retained entity
    App-->>API: PipelineDefinitionResult
    API-->>UI: 201 + Location + id
    UI-->>User: navigate to inspection view
~~~

## Interpretation Notes

- Authorization precedes the persistence effect.
- Registration creates an independent server-generated identity and commits one row atomically.
- The response contains the governed minimal representation.

## Unresolved / Deferred Boundaries

- Login/identity-management UX is outside Increment 1.
- No idempotency-key, deduplication, update, execution, or cross-system side effect is implied.
