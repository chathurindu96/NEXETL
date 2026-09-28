# 27 — WP-01 to WP-18 Dependency Diagram

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the exact governed work-package predecessor structure for Increment 1.

## Scope

Increment 1

## Governed Sources

- NEXETL-PLAN-001 v0.1 / Approved
- NEXETL Project State v0.7 / Approved

## Mermaid Diagram

~~~mermaid
flowchart TD
    WP01["WP-01<br/>Repository and Development Foundation"]
    WP02["WP-02<br/>Backend/Django Bootstrap Foundation"]
    WP03["WP-03<br/>Configuration and Startup Validation"]
    WP04["WP-04<br/>PostgreSQL and Local Persistence Foundation"]
    WP05["WP-05<br/>Pipeline Definition Domain/Application Foundation"]
    WP06["WP-06<br/>Persistence Adapter and Initial Migration"]
    WP07["WP-07<br/>Authentication, Session and CSRF Integration"]
    WP08["WP-08<br/>Capability Authorization Integration"]
    WP09["WP-09<br/>External Error-Contract Foundation"]
    WP10["WP-10<br/>Pipeline Definition REST API"]
    WP11["WP-11<br/>OpenAPI Contract Completion"]
    WP12["WP-12<br/>SvelteKit Application Foundation"]
    WP13["WP-13<br/>Pipeline Definition Registration UI"]
    WP14["WP-14<br/>Pipeline Definition Inspection UI"]
    WP15["WP-15<br/>Frontend Auth/Error/Security-State Integration"]
    WP16["WP-16<br/>Cross-Layer Automated Test Completion"]
    WP17["WP-17<br/>End-to-End and Security Validation"]
    WP18["WP-18<br/>Increment Completion and Evidence Collection"]
    WP01 --> WP02
    WP01 --> WP03
    WP02 --> WP03
    WP01 --> WP04
    WP03 --> WP04
    WP02 --> WP05
    WP04 --> WP06
    WP05 --> WP06
    WP02 --> WP07
    WP03 --> WP07
    WP04 --> WP07
    WP05 --> WP08
    WP07 --> WP08
    WP02 --> WP09
    WP03 --> WP09
    WP05 --> WP10
    WP06 --> WP10
    WP07 --> WP10
    WP08 --> WP10
    WP09 --> WP10
    WP09 --> WP11
    WP10 --> WP11
    WP01 --> WP12
    WP03 --> WP12
    WP07 --> WP12
    WP10 --> WP13
    WP11 --> WP13
    WP12 --> WP13
    WP10 --> WP14
    WP11 --> WP14
    WP12 --> WP14
    WP07 --> WP15
    WP08 --> WP15
    WP09 --> WP15
    WP12 --> WP15
    WP13 --> WP15
    WP14 --> WP15
    WP06 --> WP16
    WP07 --> WP16
    WP08 --> WP16
    WP09 --> WP16
    WP10 --> WP16
    WP11 --> WP16
    WP12 --> WP16
    WP13 --> WP16
    WP14 --> WP16
    WP15 --> WP16
    WP11 --> WP17
    WP13 --> WP17
    WP14 --> WP17
    WP15 --> WP17
    WP16 --> WP17
    WP17 --> WP18
~~~

## Interpretation Notes

- Every solid edge represents an explicit PLAN-001 predecessor; number adjacency alone creates no edge.
- WP-16 predecessors WP-06 through WP-15 are applicable as relevant, exactly as qualified by PLAN-001.
- Project State records WP-01 complete and WP-02 not started at the baseline used for this catalogue.

## Unresolved / Deferred Boundaries

- The diagram does not authorize a work package or change its governed status.
- Timing, staffing and parallel-execution choices are not inferred from the predecessor graph.
