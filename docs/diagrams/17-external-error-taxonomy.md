# 17 — External Error Taxonomy

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the governed semantic error families without presenting them as the complete error-code catalogue.

## Scope

Platform

## Governed Sources

- NEXETL-DOC-020 / Approved
- NEXETL-ADR-007 / Accepted

## Mermaid Diagram

~~~mermaid
flowchart TB
    ROOT["External Error Semantic Families"]
    ROOT --> V["Validation / Input"]
    ROOT --> A1["Authentication"]
    ROOT --> A2["Authorization"]
    ROOT --> N["Requested Resource / Not Visible"]
    ROOT --> C["Conflict / Concurrency / State"]
    ROOT --> D["Domain / Application / Use Case"]
    ROOT --> X["Dependency / External System"]
    ROOT --> I["Server / Runtime / Internal"]
~~~

## Interpretation Notes

- These are semantic families, not the complete error-code catalogue.
- Stable external codes use the governed NEXETL naming convention.
- HTTP status, code, message, and optional detail are mapped at the centralized boundary.

## Unresolved / Deferred Boundaries

- Endpoint-specific codes beyond the approved Increment 1 subset remain future governed work.
- Information-disclosure policy may deliberately collapse some internal distinctions.
