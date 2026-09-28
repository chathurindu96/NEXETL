# 05 — Frontend Architecture

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the approved Increment 1 SvelteKit routes, UI responsibilities, API-client boundary, and browser security relationship.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-018 / Approved
- NEXETL-ADR-003 / Accepted
- NEXETL-ADR-004 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    B["Browser"]
    subgraph SK["SvelteKit Frontend"]
      R1["/pipelines/new"]
      R2["/pipelines/[pipelineDefinitionId]"]
      UI["Page / Feedback Components"]
      CLIENT["Frontend API Client"]
      CSRF["CSRF Bootstrap / Header Handling"]
      R1 --> UI
      R2 --> UI
      UI --> CLIENT
      CSRF --> CLIENT
    end
    REST["Django / DRF REST Boundary"]
    AUTH["Server-Managed Session + CSRF"]
    B --> SK
    CLIENT -->|credentials included| REST
    REST --> AUTH
    AUTH --> REST
~~~

## Interpretation Notes

- SvelteKit owns browser routing and task-state presentation.
- The API client includes session credentials and applies CSRF handling to state-changing requests.
- The backend remains authoritative for authentication and authorization.

## Unresolved / Deferred Boundaries

- No BFF, OAuth/OIDC/SSO, frontend authorization authority, or unrelated dashboard is introduced.
- SSR requirements and broader state-management frameworks remain unselected.
