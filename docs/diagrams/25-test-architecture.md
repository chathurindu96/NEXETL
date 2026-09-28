# 25 — Test Architecture

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the governed Increment 1 test layers and their approved tools.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-025 / Approved
- NEXETL-DES-001 v1.0 / Approved
- NEXETL-PLAN-001 v0.1 / Approved

## Mermaid Diagram

~~~mermaid
flowchart TD
    subgraph Backend["Backend test layers"]
        BUnit["Unit"]
        BDomain["Application / domain"]
        BPersist["Persistence integration"]
        BApi["API"]
        BAuthn["Authentication / CSRF"]
        BAuthz["Authorization"]
        BError["Error contract"]
        BConfig["Configuration"]
        BTools["pytest + pytest-django<br/>DRF testing facilities"]
        BTools --> BUnit
        BTools --> BDomain
        BTools --> BPersist
        BTools --> BApi
        BTools --> BAuthn
        BTools --> BAuthz
        BTools --> BError
        BTools --> BConfig
    end
    subgraph Frontend["Frontend test layers"]
        FUnit["Unit / component"]
        FFeature["Feature / page / error-state"]
        FTools["Vitest<br/>Testing Library for Svelte"]
        FTools --> FUnit
        FTools --> FFeature
    end
    subgraph Integrated["Integrated test layers"]
        E2E["End-to-end"]
        A11y["Accessibility"]
        ITools["Playwright + axe-core"]
        ITools --> E2E
        ITools --> A11y
    end
    Backend --> Integrated
    Frontend --> Integrated
~~~

## Interpretation Notes

- The layers collectively cover input, behavior, persistence, security controls, error contracts, frontend states and cross-layer retention.
- Tool labels show governed applicability; they do not imply every tool must be used for every test layer.
- Successful execution status alone is not proof of ETL correctness.

## Unresolved / Deferred Boundaries

- Future execution-engine, connector and broader platform test suites are outside Increment 1.
- This view does not establish CI provider or production test-environment infrastructure.
