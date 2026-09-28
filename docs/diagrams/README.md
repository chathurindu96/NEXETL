# NEXETL Diagram Catalogue

This directory is the derived visual reference layer for the current governed NEXETL baseline. It contains Mermaid source in Markdown so the catalogue remains inspectable, reviewable and portable.

Google Drive `NexETL/` remains authoritative. These diagrams do not independently establish or modify requirements, architecture, design, planning, governance or implementation authorization. If any diagram conflicts with an Approved document, Accepted ADR, Approved Detailed Design or Approved implementation plan, the governed source artifact wins.

The local files in `docs/diagrams/` and the matching files in Google Drive `NexETL/Diagrams/` should remain content-identical. Future governed changes may require a controlled refresh of this derived catalogue. `NexETL/OLD/` is excluded from all source use.

> Derived visualization only. Governed source documents remain authoritative.

## Catalogue

| No. | File | Title | Mermaid type | Scope |
|---:|---|---|---|---|
| 01 | `01-system-context.md` | NEXETL System Context | flowchart | Platform |
| 02 | `02-platform-container-architecture.md` | Platform Container Architecture | flowchart | Both |
| 03 | `03-platform-component-architecture.md` | Platform Component Architecture | flowchart | Platform |
| 04 | `04-backend-module-dependency.md` | Backend Module Dependency | flowchart | Increment 1 |
| 05 | `05-frontend-architecture.md` | Frontend Architecture | flowchart | Increment 1 |
| 06 | `06-repository-structure.md` | Core Monorepo / Repository Structure | flowchart | Both |
| 07 | `07-increment-1-class-domain-model.md` | Increment 1 UML Class / Domain Model | classDiagram | Increment 1 |
| 08 | `08-increment-1-physical-eer.md` | Increment 1 Physical EER | erDiagram | Increment 1 |
| 09 | `09-domain-to-persistence-mapping.md` | Domain to Persistence Mapping | flowchart | Increment 1 |
| 10 | `10-register-pipeline-definition-sequence.md` | Register Pipeline Definition Sequence | sequenceDiagram | Increment 1 |
| 11 | `11-inspect-pipeline-definition-sequence.md` | Inspect Pipeline Definition Sequence | sequenceDiagram | Increment 1 |
| 12 | `12-authentication-csrf-sequence.md` | Authentication and CSRF Sequence | sequenceDiagram | Increment 1 |
| 13 | `13-authorization-decision-flow.md` | Authorization Decision Flow | flowchart | Increment 1 |
| 14 | `14-api-request-processing-flow.md` | API Request Processing Flow | flowchart | Increment 1 |
| 15 | `15-increment-1-rest-api-resource-map.md` | Increment 1 REST API Resource Map | flowchart | Increment 1 |
| 16 | `16-external-error-translation-flow.md` | External Error Translation Flow | flowchart | Both |
| 17 | `17-external-error-taxonomy.md` | External Error Taxonomy | flowchart | Platform |
| 18 | `18-configuration-resolution.md` | Configuration Resolution | flowchart | Both |
| 19 | `19-security-trust-boundaries.md` | Security Trust Boundaries | flowchart | Both |
| 20 | `20-security-control-flow.md` | Security Control Flow | flowchart | Increment 1 |
| 21 | `21-frontend-navigation-flow.md` | Frontend Navigation Flow | flowchart | Increment 1 |
| 22 | `22-frontend-ui-state-machine.md` | Frontend UI State Machine | stateDiagram-v2 | Increment 1 |
| 23 | `23-local-development-topology.md` | Local Development Topology | flowchart | Increment 1 |
| 24 | `24-increment-1-runtime-topology.md` | Increment 1 Runtime Topology | flowchart | Both |
| 25 | `25-test-architecture.md` | Test Architecture | flowchart | Increment 1 |
| 26 | `26-increment-1-e2e-verification-sequence.md` | Increment 1 End-to-End Verification | sequenceDiagram | Increment 1 |
| 27 | `27-work-package-dependency.md` | WP-01 to WP-18 Dependency Diagram | flowchart | Increment 1 |
| 28 | `28-implementation-waves.md` | Implementation Waves | flowchart | Increment 1 |
| 29 | `29-implementation-change-control.md` | Implementation Change Control | flowchart | Increment 1 |
| 30 | `30-increment-1-requirement-traceability.md` | Increment 1 Requirement Traceability | flowchart | Increment 1 |
| 31 | `31-platform-wide-conceptual-eer.md` | NEXETL Platform-Wide Conceptual EER / Data Model | erDiagram | Platform |

## Maintenance Boundary

- Refresh a diagram only from the current governed sources named in that diagram.
- Preserve unresolved and deferred subjects; do not use a visualization to settle them.
- Keep Diagram 08 as the concrete physical Increment 1 EER.
- Keep Diagram 31 conceptual and platform-wide; future physical persistence remains subject to later Detailed Design.
- Update the local and Drive copies together and record identity and validation results in `MANIFEST.md`.
