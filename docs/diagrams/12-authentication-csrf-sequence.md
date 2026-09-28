# 12 — Authentication and CSRF Sequence

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the approved browser session and CSRF protection flow for Increment 1.

## Scope

Increment 1

## Governed Sources

- NEXETL-ADR-004 / Accepted
- NEXETL-DES-001 v1.0 / Approved

## Mermaid Diagram

~~~mermaid
sequenceDiagram
    actor User
    participant Browser
    participant UI as SvelteKit
    participant API as Django / DRF
    participant Session as Session Authentication
    participant CSRF as CSRF Enforcement
    User->>Browser: Open protected workflow
    Browser->>UI: Load application route
    UI->>API: GET /api/security/csrf/
    API-->>Browser: 204 + CSRF cookie
    Note over Browser,Session: Existing authenticated session is server-managed
    Browser->>API: POST + session cookie + CSRF header
    API->>Session: authenticate session credential
    Session-->>API: authenticated principal
    API->>CSRF: validate cookie/header token
    CSRF-->>API: accepted
    API-->>UI: continue governed request
~~~

## Interpretation Notes

- The session credential is carried in an HttpOnly cookie and authoritative state remains server-side.
- CSRF bootstrap issues the token needed for later state-changing cookie-authenticated requests.
- The frontend includes credentials but does not store the session credential.

## Unresolved / Deferred Boundaries

- Identity lifecycle and login UX are not defined by Increment 1.
- OAuth2, OIDC, SSO, and API-token flows are intentionally absent.
