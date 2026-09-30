# NEXETL-REG-001 — Architecture Decision Register


Project: NEXETL — Next Generation ETL Platform
Register ID: NEXETL-REG-001
Version: 0.2
Status: Approved
Last Updated: 2026-09-25
Owner: 00 Project Governance
Approval Authority: Product/Architecture Owner
Governing Source: NEXETL-DOC-000 v1.2 — Approved
ADR Governance: NEXETL ADR Governance Standard v0.2 — Approved
Baseline: CURRENT NEXETL governed documentation baseline


## 1. Purpose
This register is the lightweight operational global index and lifecycle/status record for formally allocated CURRENT-baseline NEXETL Architecture Decision Records.


The ADR document is the decision record and authority for its architecture decision. REG-001 is the global index and lifecycle register for allocated ADRs; it does not itself make or approve architecture decisions, and it is not a Candidate ADR backlog, TBD register, implementation task list, or Detailed Design register.


## 2. Register Rules
- Record an ADR only after formal ADR processing is initiated and an NEXETL-ADR-XXX identifier is allocated.
- Candidate ADR subjects remain outside REG-001 merely because they exist; they appear only after formal ADR processing is initiated and an identifier is allocated.
- Candidate subjects do not consume ADR identifiers.
- ADR identifiers are never reused or silently renumbered.
- Status changes shall reflect the authoritative ADR.
- Accepted, Rejected, Superseded, and Deprecated ADRs remain in the register for history.
- Supersession relationships shall be recorded in both directions.
- A short decision summary must remain descriptive and must not substitute for the complete ADR.
- Supported lifecycle statuses for allocated ADRs are Proposed, Under Review, Accepted, Rejected, Superseded, and Deprecated.
- Proposed or Under Review entries are non-authoritative.
- Decision Scope / Applicable Increment records whether an allocated ADR is Platform-wide or applies to a clearly identified implementation increment.
- The register supports the operating model: Discuss locally -> Decide explicitly -> Record globally -> Reference thereafter -> Supersede rather than erase, without making REG-001 an approval bottleneck.
- NEXETL/OLD/ entries are not imported into this CURRENT-baseline register unless separately authorized through governance.


## 3. Register Fields
Each ADR entry tracks:
- ADR ID
- Title
- Status
- Decision Scope / Applicable Increment
- Date allocated or created
- Decision/approval date where applicable
- Supersedes
- Superseded By
- Related governed artifact/reference
- Short decision summary


## 4. Architecture Decision Register


Seven ADRs are currently allocated for the CURRENT NEXETL baseline. NEXETL-ADR-001 is Accepted and authoritative for REPO-TBD-001 — Repository Topology. NEXETL-ADR-002 is Accepted and authoritative for REPO-TBD-003 — Dependency and Package Management Strategy. NEXETL-ADR-003 is Accepted and authoritative for FE-TBD-001 and the architecture-significant application/routing portion of FE-TBD-002 only. NEXETL-ADR-004 is Accepted and authoritative for SEC-TBD-002, API-TBD-010 and the architecture-significant authentication/session portion of FE-TBD-015 only. NEXETL-ADR-005 is Accepted and authoritative for B-06 / SEC-TBD-004, API-TBD-011 and only the architecture-significant portion of BACK-TBD-011. NEXETL-ADR-006 is Accepted and authoritative for B-07 / CFG-TBD-001 only. NEXETL-ADR-007 is Accepted and authoritative for B-08 / ERR-TBD-001, ERR-TBD-002, API-TBD-003 and only the architecture-significant external/semantic-boundary portion of BACK-TBD-023.


| ADR ID | Title | Status | Decision Scope / Applicable Increment | Date allocated or created | Decision/approval date | Supersedes | Superseded By | Related governed artifact/reference | Short decision summary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NEXETL-ADR-001 | Repository Topology | Accepted | Platform-wide; Increment 1 — Pipeline Definition Registration and Inspection Foundation | 2026-09-25 | 2026-09-25 | None | None | NEXETL-DOC-024; NEXETL-PRE-ADR-ANALYSIS-REPO-TBD-001 | Accepted decision: Core Monorepo for the closely coupled NEXETL core platform; resolves REPO-TBD-001 only. |
| NEXETL-ADR-002 | Dependency and Package Management Strategy | Accepted | Platform-wide engineering/dependency-management foundation; Increment 1 — Pipeline Definition Registration and Inspection Foundation | 2026-09-25 | 2026-09-25 | None | None | NEXETL-ADR-001; NEXETL-DOC-024; NEXETL-PRE-ADR-ANALYSIS-REPO-TBD-003 | Accepted decision: uv + committed Python lock state; npm + committed npm lockfile; no additional workspace/orchestrator initially; separate backend/frontend dependency ownership; resolves REPO-TBD-003 only. |
| NEXETL-ADR-003 | Svelte Application and Routing Foundation | Accepted | Platform-wide frontend application/routing foundation; Increment 1 — Pipeline Definition Registration and Inspection Foundation | 2026-09-25 | 2026-09-25 | None | None | NEXETL-ADR-001; NEXETL-ADR-002; NEXETL-DOC-018; NEXETL-PRE-ADR-ANALYSIS-FE-TBD-001-002 | Accepted decision: SvelteKit application foundation with framework-managed browser routing; client-side interactive rendering sufficient for Increment 1; no SSR requirement; Django/DRF REST/OpenAPI remains the backend/API boundary; resolves FE-TBD-001 and the architecture-significant application/routing portion of FE-TBD-002 only. |
| NEXETL-ADR-004 | Authentication and Security-Context Mechanism | Accepted | Platform-wide authentication/security-context foundation for the currently supported browser-oriented human-user interaction model; Increment 1 — Pipeline Definition Registration and Inspection Foundation | 2026-09-25 | 2026-09-25 | None | None | NEXETL-ADR-001; NEXETL-ADR-002; NEXETL-ADR-003; NEXETL-DOC-010; NEXETL-DOC-017; NEXETL-DOC-018; NEXETL-PRE-ADR-ANALYSIS-SEC-TBD-002-API-TBD-010-FE-TBD-015 | Accepted decision: Django/DRF server-managed session authentication with secure cookie-carried session credential; Django/DRF establishes authoritative authenticated principal/security context; session credential not intentionally exposed to browser JavaScript; HttpOnly applicable; CSRF required for state-changing cookie-authenticated requests; SvelteKit remains browser client with no BFF; direct SvelteKit → Django/DRF REST interaction preserved. Resolves SEC-TBD-002, API-TBD-010 and the architecture-significant authentication/session portion of FE-TBD-015 only. B-06 is outside ADR-004 scope and is separately resolved by Accepted NEXETL-ADR-005. |


| NEXETL-ADR-005 | Authorization and Resource-Ownership Model | Accepted | Platform-wide authorization foundation for protected backend capabilities; initially applicable to Increment 1 — Pipeline Definition Registration and Inspection Foundation | 2026-09-25 | 2026-09-25 | None | None | NEXETL-ADR-004; NEXETL-DOC-010; NEXETL-DOC-016; NEXETL-DOC-017; NEXETL-DOC-018; NEXETL-PRE-ADR-ANALYSIS-SEC-TBD-004-API-TBD-011 | Accepted decision: capability-oriented backend authorization using ADR-004 authenticated principal/security context + requested protected action + relevant resource/context; backend-authoritative and deny-by-default; authorization before protected effects; identifier/direct-resource bypass prohibited; frontend authorization-aware presentation non-authoritative; no Pipeline Definition ownership, RBAC role taxonomy, permission matrices, tenancy or sharing/delegation introduced. Resolves SEC-TBD-004, API-TBD-011 and only the architecture-significant portion of BACK-TBD-011. B-08 remains unresolved. |
| NEXETL-ADR-006 | Configuration Source and Precedence Architecture | Accepted | Platform-wide configuration source/precedence foundation for bootstrap, deployment and managed configuration boundaries; initially applicable to Increment 1 — Pipeline Definition Registration and Inspection Foundation | 2026-09-25 | 2026-09-25 | None | None | NEXETL-DOC-020; NEXETL-DOC-027; NEXETL-PRE-ADR-ANALYSIS-CFG-TBD-001 | Accepted decision: bounded hybrid, concern-specific configuration resolution; one semantic owner and explicit allowed-source set per concern; no universal cross-category precedence stack; startup precedence safe documented default < explicit deployment/environment value; persisted managed product/domain configuration does not generically override bootstrap configuration; secrets remain outside ordinary precedence; centralized backend resolution; browser-safe frontend configuration only; process-lifetime-stable bootstrap configuration by default. Resolves CFG-TBD-001 only. CFG-TBD-002 through CFG-TBD-006, RUNSTD-TBD-008, Connector/Extension-specific configuration mechanics, secret-provider architecture and B-08 remain unresolved. |
| NEXETL-ADR-007 | External Error Taxonomy, Stable Error Codes and API Error Contract | Accepted | Platform-wide external REST error-contract, semantic error-taxonomy and stable external error-code architecture; initially applicable to Increment 1 — Pipeline Definition Registration and Inspection Foundation | 2026-09-25 | 2026-09-25 | None | None | NEXETL-DOC-016; NEXETL-DOC-017; NEXETL-DOC-020; NEXETL-DOC-021; NEXETL-DOC-026; NEXETL-PRE-ADR-ANALYSIS-ERR-TBD-001-002-API-TBD-003 | Accepted decision: standard HTTP protocol semantics plus globally unique stable symbolic NEXETL codes; one common external error core; governed class-specific structured details; multi-issue validation details; safe human-readable messages not used as stable machine contracts; optional safe correlation reference; centralized internal-to-external translation/sanitization; reusable OpenAPI components; compatibility-governed code/schema/HTTP mappings; Problem Details compatible but not mandatory. Resolves ERR-TBD-001, ERR-TBD-002, API-TBD-003 and only the architecture-significant external/semantic-boundary portion of BACK-TBD-023. ERR-TBD-003/004, applicable observability/correlation TBDs, RUNSTD-TBD-010 and Detailed Design exclusions remain unresolved. |
| NEXETL-ADR-008 | Built-in Connector Runtime and Secret Boundary | Accepted | Platform-wide connector runtime foundation; Increment 3 — End-to-End Pipeline Platform | 2026-09-30 | 2026-09-30 | None | None | NEXETL-DOC-010; NEXETL-DOC-013; NEXETL-DOC-014; NEXETL-DOC-020; NEXETL-DOC-027 | Capability-oriented trusted built-in adapters, minimal logical schema contract, opaque secret references and replaceable encrypted local-development secret provider. |
| NEXETL-ADR-009 | Executable Pipeline Graph and Bounded Batch Model | Accepted | Pipeline execution foundation; Increment 3 — End-to-End Pipeline Platform | 2026-09-30 | 2026-09-30 | None | None | NEXETL-DOC-011; NEXETL-DOC-012; NEXETL-DOC-015; NEXETL-DOC-022 | Executable DAG with named ports, immutable normalized versions, deterministic compilation, minimal logical types, bounded batches and disk-backed bounded stateful staging. |
| NEXETL-ADR-010 | PostgreSQL Run Queue, Worker and Scheduler | Accepted | Runtime control-plane foundation; Increment 3 — End-to-End Pipeline Platform | 2026-09-30 | 2026-09-30 | None | None | NEXETL-DOC-019; NEXETL-DOC-020; NEXETL-DOC-021; NEXETL-DOC-022; NEXETL-DOC-027 | PostgreSQL-backed durable Run queue, transactional SKIP LOCKED claiming, dedicated worker and scheduler commands, cooperative cancellation and immutable-version retries. |
## 5. Current Register Summary
Allocated ADRs: 7
Proposed: 0
Under Review: 0
Accepted: 7
Rejected: 0
Superseded: 0
Deprecated: 0


## 6. Maintenance
Update this register when:
- an ADR identifier is allocated;
- an ADR status changes;
- an ADR is accepted or rejected;
- an ADR is deprecated or superseded;
- a supersession relationship changes;
- related governed documents materially change.


Register maintenance shall not be used to create or approve an architecture decision, allocate an identifier merely for a Candidate subject, or turn REG-001 into a Candidate backlog. Historical ADR entries remain retained when Superseded or Deprecated.


## 7. Change History
Version 0.2 — Approved — 2026-09-25
Approval: Explicitly approved by the Product/Architecture Owner and promoted in place from Version 0.2 / Draft to Version 0.2 / Approved. This approval establishes REG-001 as the Approved operational global index and lifecycle register for formally allocated NEXETL Architecture Decision Records only. It does not allocate or create an ADR, accept an ADR, insert Candidate ADR subjects into REG-001, resolve architecture/UL/TBD/quantitative dependencies, authorize Detailed Design, create or authorize PLAN-001, open Gate 5, or authorize implementation.
Version 0.2 — Draft — 2026-09-25
Controlled activation and compatibility revision under NEXETL-DOC-000 v1.2 Approved and NEXETL ADR Governance Standard v0.2 Approved. Establishes REG-001 as the lightweight operational global index/lifecycle register for formally allocated ADRs; adds Decision Scope / Applicable Increment and allocation/decision-date compatibility; preserves Candidate subjects outside the register until formal ADR allocation; preserves all governed lifecycle statuses and supersession/history navigation. Zero ADR identifiers are allocated and zero ADRs are Accepted. No Candidate subject, architecture/UL/TBD/quantitative dependency, Detailed Design, PLAN-001, Gate 5 condition, or implementation authorization is resolved by this revision.
Version 0.1 — Draft — 2026-09-24
Initial CURRENT-baseline Architecture Decision Register with zero allocated ADRs.


End of NEXETL-REG-001
