# 23 — Local Development Topology

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Faithfully reproduce the approved DES-001 local development topology.

## Scope

Increment 1

## Governed Sources

- NEXETL-ADR-006 / Accepted
- NEXETL-DES-001 v1.0 / Approved
- NEXETL-PLAN-001 v0.1 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    Browser["Browser<br/>localhost:5173"] --> Frontend["SvelteKit dev server<br/>:5173"]
    Frontend --> Proxy["/api proxy"]
    Proxy --> Backend["Django / DRF<br/>:8000"]
    Backend --> Database["PostgreSQL container<br/>:5432"]
    FrontendEnv["Documented frontend environment values"] --> Frontend
    BackendEnv["Documented backend environment values"] --> Backend
    SecretInput["Protected secret inputs"] --> Backend
    DatabaseEnv["Documented database environment values"] --> Database
~~~

## Interpretation Notes

- Browser traffic is served by the SvelteKit development server, with `/api` proxied to Django/DRF.
- Django/DRF connects to the local PostgreSQL container.
- Configuration inputs are shown by responsibility and do not define one universal precedence hierarchy.

## Unresolved / Deferred Boundaries

- The diagram is local-development topology, not production deployment architecture.
- It does not introduce a message broker, scheduler, cache, workflow engine or separately deployed logical module.
