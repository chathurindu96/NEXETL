# NEXETL-ADR-008 — Built-in Connector Runtime and Secret Boundary

Title: Built-in Connector Runtime and Secret Boundary
Version: 0.1
Status: Accepted
Date: 2026-09-30
Decision Owners: Product/Architecture Owner
Decision Scope: Complete Pipeline Platform increment; connector execution, discovery, connection configuration and secret handling.
Applicable Increment: Increment 3 — End-to-End Pipeline Platform.
Dependencies: NEXETL-ADR-004 through NEXETL-ADR-007; NEXETL-DOC-010; NEXETL-DOC-013; NEXETL-DOC-014; NEXETL-DOC-020; NEXETL-DOC-027.

## Context

DOC-014 intentionally deferred the Connector contract, capability model, driver isolation and secret-provider mechanism. The authorized increment requires configured Connections, discovery, preview and real database reads/writes for PostgreSQL, SQL Server, MySQL and MariaDB.

## Problem / Decision Required

Select a bounded connector runtime contract, initial isolation model and replaceable secret boundary without coupling Pipeline logic to database products or returning credentials through APIs.

## Options Considered

1. Vendor conditionals embedded in Pipeline services.
2. Out-of-process connector plug-ins from the first increment.
3. Capability-oriented adapters for trusted built-in connectors, with an explicit future isolation boundary.

## Accepted Decision

NEXETL will use capability-oriented connector adapters owned by the connector boundary. Adapters expose typed operations for connection testing, schema/dataset/column discovery, bounded preview, batch reads and batch writes. Pipeline/runtime code resolves an adapter through a registry and never branches on database product.

The initial PostgreSQL, SQL Server, MySQL and MariaDB adapters are trusted built-in modules running inside the dedicated worker or bounded API discovery operation. Optional vendor drivers fail with a stable capability/driver-unavailable error when not installed; unsupported capabilities are declared rather than simulated. Third-party/untrusted connector loading remains out of scope and must receive a later isolation decision.

Configured Connection metadata stores non-secret configuration separately from opaque secret references. Secret values are handled through a `SecretProvider` port. The local-development provider encrypts values before persistence and returns them only to authorized backend/runtime code. Production deployments may replace it with an environment, vault or managed-secret provider without changing Connection or Pipeline contracts. GET representations never contain secret values, logs must redact them, and Pipeline nodes reference Connection UUIDs only.

The shared schema contract is deliberately minimal: field name, logical type, native type, nullable, ordinal and bounded metadata. Vendor-specific details remain adapter-owned metadata.

## Consequences

- Connector behavior remains replaceable and contract-testable.
- Built-in adapters share the modular-monolith release lifecycle and dependency environment.
- The first implementation does not provide hostile-code isolation or dynamic third-party installation.
- Connection tests/discovery/preview are bounded by timeout, row and payload limits.

## Validation Criteria

Contract tests cover capabilities, secret non-disclosure, error sanitization, bounded preview and adapter resolution. PostgreSQL receives real integration coverage. Other products receive contract coverage unless their external services are available, and must not be reported as integration-tested otherwise.

## Approval Record

Decision: Accepted through the Product Owner's explicit 2026-09-30 fast-track authorization for the Complete End-to-End Pipeline Platform increment.
