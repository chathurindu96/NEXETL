# Increment 3 Detailed Design — Complete Pipeline Platform

Status: Approved for implementation by explicit Product Owner fast-track authorization dated 2026-09-30.

## Scope and boundaries

This increment extends the existing modular monolith with configured database Connections, a typed node registry, schema-aware executable Pipeline Versions, asynchronous Runs, worker/scheduler processes and operational SvelteKit routes. Django/DRF remains the control plane; runtime rows stay in the worker data plane. It does not introduce streaming, CDC, Spark, Kafka, Airflow, Kubernetes, tenancy, billing or arbitrary third-party code execution.

## Modules

- `pipelines.connections`: Connection application services, secret-provider port and database adapter registry.
- `pipelines.registry`: immutable node metadata, ports, configuration schemas and executor keys.
- `pipelines.schema`: logical fields, propagation and compatibility issues.
- `pipelines.runtime.compiler`: deterministic graph validation and topological plan compilation.
- `pipelines.runtime.executors`: one executor strategy per node family.
- `pipelines.runtime.coordinator`: Run lifecycle, batches, metrics, events and cancellation.
- `pipelines.runtime.claiming`: short transactional PostgreSQL claiming/lease operations.
- Django management commands provide separately runnable worker and scheduler processes.

## Persistence

New normalized records cover Connection, encrypted local secret, Pipeline Version and its nodes/edges, Pipeline Run, Pipeline Node Run, bounded Run Event and Pipeline Schedule. Design nodes gain `kind`, versioned configuration and cached schemas. Edges gain source/target ports. Existing nodes and edges migrate to compatible default kinds and ports without resetting data.

Heterogeneous node configuration, inferred schema, metrics and safe structured event context use validated JSONB. Identity, relationships, lifecycle state, timestamps and queue/schedule coordination remain relational and indexed.

## API

REST resources are added under `/api/connections/`, `/api/node-types/`, and nested Pipeline resources for versions, runs and schedules. Connection test/discovery/preview actions remain bounded operations with stable errors. Mutations use existing session authentication, CSRF and backend capability checks. Secret input is write-only.

## Execution

Run creation validates the editable design, creates an immutable version in the same transaction and enqueues a Run. The compiler checks ports, acyclicity, required configuration, propagated schemas and adapter capabilities. The worker claims one Run, executes topologically, records Node Runs and events, and commits connector-owned target transactions. Downstream work is skipped after failure or cancellation.

Rows move in configured batches. Streaming transforms remain batch-local. Aggregate, join, sort, distinct and deduplicate use bounded temporary staging and fail safely when limits are exceeded. Preview defaults to 50 rows, is hard-capped, timed and payload-limited.

## Frontend

The Pipeline workspace exposes Overview, Design, Runs, Schedules and Settings. Connections are distinct from Connector definitions. Inspector editors are purpose-specific and schema/preview/validation aware. Run Details renders the immutable version graph with Node Run state. Home and Library use real operational data.

## Security and operations

Passwords are never represented by Connection GET endpoints, Pipeline configuration, events or logs. Runtime logging carries correlation identifiers and stable event names. Worker and scheduler health expectations are process-specific. PostgreSQL integration evidence uses controlled synthetic data only.

## Verification

Required evidence includes migration upgrade, domain/compiler/executor/claiming/scheduler tests, real PostgreSQL source-to-target and join scenarios, API security tests, frontend component tests, Playwright lifecycle tests, accessibility checks, production build, secret scan and clean Git state.
