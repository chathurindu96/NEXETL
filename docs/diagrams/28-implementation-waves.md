# 28 — Implementation Waves

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the governed Increment 1 progression and the work packages assigned to each PLAN-001 wave.

## Scope

Increment 1

## Governed Sources

- NEXETL-PLAN-001 v0.1 / Approved
- NEXETL Project State v0.7 / Approved

## Mermaid Diagram

~~~mermaid
flowchart LR
    A["Wave A — Foundation<br/>WP-01 Repository and Development Foundation<br/>WP-02 Backend/Django Bootstrap Foundation<br/>WP-03 Configuration and Startup Validation<br/>WP-04 PostgreSQL and Local Persistence Foundation"]
    B["Wave B — Domain and Persistence<br/>WP-05 Pipeline Definition Domain/Application Foundation<br/>WP-06 Persistence Adapter and Initial Migration"]
    C["Wave C — Security, Errors and API<br/>WP-07 Authentication, Session and CSRF Integration<br/>WP-08 Capability Authorization Integration<br/>WP-09 External Error-Contract Foundation<br/>WP-10 Pipeline Definition REST API<br/>WP-11 OpenAPI Contract Completion"]
    D["Wave D — Frontend<br/>WP-12 SvelteKit Application Foundation<br/>WP-13 Pipeline Definition Registration UI<br/>WP-14 Pipeline Definition Inspection UI<br/>WP-15 Frontend Auth/Error/Security-State Integration"]
    E["Wave E — Convergence and Evidence<br/>WP-16 Cross-Layer Automated Test Completion<br/>WP-17 End-to-End and Security Validation<br/>WP-18 Increment Completion and Evidence Collection"]
    A --> B --> C --> D --> E
~~~

## Interpretation Notes

- Wave names and work-package membership reproduce PLAN-001 terminology.
- The left-to-right progression is a delivery view; the exact executable constraints remain the predecessor relationships in PLAN-001 and Diagram 27.
- The current baseline has completed WP-01 only; this diagram does not begin WP-02.

## Unresolved / Deferred Boundaries

- The wave view does not add dates, duration, staffing or release commitments.
- Future increments are outside this Increment 1 plan.
