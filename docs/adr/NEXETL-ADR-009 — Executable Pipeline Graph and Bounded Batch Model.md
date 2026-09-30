# NEXETL-ADR-009 — Executable Pipeline Graph and Bounded Batch Model

Title: Executable Pipeline Graph and Bounded Batch Model
Version: 0.1
Status: Accepted
Date: 2026-09-30
Decision Owners: Product/Architecture Owner
Decision Scope: Complete Pipeline Platform increment; graph semantics, immutable versions, schema and execution data transport.
Applicable Increment: Increment 3 — End-to-End Pipeline Platform.
Dependencies: NEXETL-ADR-008; NEXETL-DOC-011; NEXETL-DOC-012; NEXETL-DOC-015; NEXETL-DOC-022.

## Context

The existing visual graph is a DAG but the approved baseline deferred its executable structure, immutable version binding, common type representation and intermediate-data strategy.

## Accepted Decision

A Pipeline Design is an editable directed acyclic graph. Edges persist source and target port identifiers. Node behavior is selected by a versioned Node Type Registry rather than distributed type switches. The compiler validates node, edge, port, configuration, schema and connector capabilities, then performs deterministic topological ordering.

Execution never uses a mutable design directly. A successful publish/run request transaction creates or reuses an immutable Pipeline Version containing normalized version nodes and edges plus a canonical snapshot. Every Pipeline Run references exactly one version.

Runtime data moves as bounded row batches. Streaming-capable nodes process one batch at a time. Stateful nodes use an execution-scoped, disk-backed staging store with explicit row/byte safety limits; exceeding a configured limit fails visibly. This initial implementation does not claim unbounded distributed sort/join/aggregate scalability. Temporary data is removed after execution and is never authoritative metadata.

The minimal logical types are string, integer, decimal, boolean, date, timestamp, binary, json and unknown, with nullable/native-type metadata. Conversions are explicit and failure is deterministic. Expressions use a parsed, allow-listed expression language; arbitrary Python and arbitrary code evaluation are prohibited.

Database targets use connector-owned transactions. APPEND, TRUNCATE_AND_LOAD and capability-gated UPSERT are explicit. Cross-system distributed ACID is not claimed.

## Consequences

- Historical Runs remain reproducible and display their original graph.
- Existing design edges migrate to `output` → `input` ports.
- Batch size and stateful staging limits are governed configuration.
- Future distributed execution can replace the batch/staging implementation behind the runtime ports.

## Validation Criteria

Compiler, schema propagation, transformation, immutable-version, batching, mapping, failure and PostgreSQL source-to-target tests must pass. Historical Version A must remain unchanged after publishing Version B.

## Approval Record

Decision: Accepted through the Product Owner's explicit 2026-09-30 fast-track authorization.
