# 03 — Platform Component Architecture

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the major approved logical platform components while preserving modular-monolith semantics.

## Scope

Platform

## Governed Sources

- NEXETL-DOC-009 / Approved

## Mermaid Diagram

~~~mermaid
flowchart TB
    subgraph Interaction["Interaction Boundary"]
      VIS["Visual Interaction"]
      API["Programmatic API"]
    end
    subgraph MM["NEXETL Modular Monolith"]
      APP["Application Coordination"]
      PIPE["Pipeline Definition & Validation"]
      INT["Integration Configuration & Capability Coordination"]
      AUTO["Automated Initiation Responsibility"]
      EXEC["Execution Coordination"]
      OPS["Operations & Diagnostics"]
      CFG["Configuration & Protected-Credential Coordination"]
      META["Platform Metadata & Governance Records"]
      EXT["Extension / Connector Boundary"]
      GOV["Security / Observability / Error Governance"]
    end
    VIS --> APP
    API --> APP
    APP --> PIPE
    APP --> INT
    APP --> AUTO
    APP --> EXEC
    APP --> OPS
    APP --> CFG
    APP --> META
    INT --> EXT
    EXEC --> EXT
    GOV -. constrains .-> APP
    GOV -. constrains .-> EXT
    EXT <--> ES["External Systems"]
~~~

## Interpretation Notes

- All components are logical responsibilities within the approved modular-monolith architecture.
- Application coordination invokes domain/capability responsibilities through governed boundaries.
- Technology-specific behavior remains behind the extension/connector boundary.

## Unresolved / Deferred Boundaries

- Exact runtime implementation for execution and automated initiation is deferred.
- Logical components do not imply separately deployed services.
