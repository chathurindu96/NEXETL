# 06 — Core Monorepo / Repository Structure

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the approved repository foundation established by WP-01 without speculative product source trees.

## Scope

Both

## Governed Sources

- NEXETL-ADR-001 / Accepted
- NEXETL-ADR-002 / Accepted
- NEXETL-DES-001 v1.0 / Approved
- NEXETL-PLAN-001 v0.1 / Approved

## Mermaid Diagram

~~~mermaid
flowchart TB
    ROOT["NEXETL Core Monorepo"]
    ROOT --> BE["backend/<br/>pyproject.toml + uv.lock + test foundations"]
    ROOT --> FE["frontend/<br/>package.json + package-lock.json + test foundations"]
    ROOT --> TEST["tests/<br/>repository-level E2E foundation"]
    ROOT --> DOCS["docs/<br/>development and derived references"]
    ROOT --> ASSET["Root Development Assets<br/>compose.yaml + .env.example + README + .gitignore"]
~~~

## Interpretation Notes

- Backend and frontend retain separate dependency ownership.
- The repository-level tests boundary owns cross-layer E2E scenarios.
- This reflects the completed WP-01 foundation, not later application code.

## Unresolved / Deferred Boundaries

- Connector/Extension source folders are deliberately omitted because their repository structure remains unapproved for this increment.
- No monorepo orchestrator or root package workspace is implied.
