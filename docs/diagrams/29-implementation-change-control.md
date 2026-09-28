# 29 — Implementation Change Control

> Derived visualization only. Governed source documents remain authoritative.

## Purpose

Show the governed response to implementation findings at increasing levels of significance.

## Scope

Increment 1

## Governed Sources

- NEXETL-DOC-000 / Approved
- NEXETL-PLAN-001 v0.1 / Approved

## Mermaid Diagram

~~~mermaid
flowchart TD
    Finding["Implementation finding"] --> Classify{"Classification"}
    Classify -->|Implementation defect| Defect["Fix in implementation"]
    Classify -->|Minor Detailed Design ambiguity| Minor["Controlled design interpretation<br/>or update if required"]
    Classify -->|Material DES contradiction| StopDesign["Stop affected work"]
    StopDesign --> ReviseDesign["Revise Detailed Design through governance"]
    Classify -->|Architecture-significant contradiction| StopArchitecture["Stop affected work"]
    StopArchitecture --> Architecture["Architecture / ADR governance"]
    Classify -->|Requirement contradiction| StopRequirement["Stop affected work"]
    StopRequirement --> Product["Product / Requirements governance"]
~~~

## Interpretation Notes

- Classification determines whether implementation correction is sufficient or controlled governance is required.
- Work affected by a material design, architecture or requirement contradiction stops before resolution.
- A controlled source update, not an informal diagram change, carries any approved baseline change.

## Unresolved / Deferred Boundaries

- This diagram does not pre-classify any future finding or bypass required owner decisions.
- Detailed approval roles and document workflows remain governed by the source artifacts.
