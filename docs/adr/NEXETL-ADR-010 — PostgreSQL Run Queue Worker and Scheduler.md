# NEXETL-ADR-010 — PostgreSQL Run Queue, Worker and Scheduler

Title: PostgreSQL Run Queue, Worker and Scheduler
Version: 0.1
Status: Accepted
Date: 2026-09-30
Decision Owners: Product/Architecture Owner
Decision Scope: Complete Pipeline Platform increment; durable dispatch, worker claiming, cancellation, retries and schedules.
Applicable Increment: Increment 3 — End-to-End Pipeline Platform.
Dependencies: NEXETL-ADR-006; NEXETL-ADR-007; NEXETL-ADR-009; NEXETL-DOC-019; NEXETL-DOC-020; NEXETL-DOC-021; NEXETL-DOC-022; NEXETL-DOC-027.

## Context

DOC-019 requires background execution but deliberately leaves queue, worker, claiming, scheduler and delivery semantics unresolved. The increment requires real asynchronous Runs and Schedules without adding a broker or workflow engine by convention.

## Options Considered

1. Execute inside HTTP requests — rejected because lifetime, scaling and duplicate-execution safety are unacceptable.
2. Add a broker/task framework — operationally capable but unnecessary for the initial modular-monolith scale and introduces infrastructure not otherwise required.
3. Use PostgreSQL as a durable control-plane queue with dedicated worker and scheduler processes.

## Accepted Decision

`PipelineRun` rows are the durable queue. A dedicated worker transaction claims eligible queued work using row locking with `SELECT FOR UPDATE SKIP LOCKED`, records worker identity/lease timestamps and commits ownership before execution. A Run can have only one active claim. HTTP handlers only validate/publish/enqueue and return.

The worker is an independently runnable Django management command. Concurrency is bounded by validated configuration. The worker emits heartbeats, observes cooperative cancellation between safe batch/node boundaries and finalizes all state transactionally. Driver calls that cannot be interrupted are documented as delayed cooperative cancellation, not hard cancellation.

Retries create a new Run referencing the same immutable Pipeline Version. Automatic operation retries are bounded and restricted to explicitly transient adapter failures. Idempotency keys prevent accidental duplicate manual submissions; target idempotency remains write-mode dependent.

The scheduler is a separate management command. It locks due enabled schedules, creates a uniquely keyed scheduled Run and advances `next_run_at` in one transaction. Cron expressions are validated and timezone-aware. Disabled schedules are ignored. This prevents duplicate enqueue across concurrent scheduler processes.

No broker, Celery, workflow engine or in-web-server poller is introduced. A later ADR may replace the queue when measured scale, isolation or operational requirements justify it.

## Consequences

- PostgreSQL carries additional short control-plane locking/query load; indexes and short transactions are mandatory.
- Runtime data never travels through the queue row or DRF.
- Web, worker and scheduler responsibilities remain separately deployable processes within the modular monolith.

## Validation Criteria

Concurrent claiming, duplicate prevention, crash/lease recovery, cooperative cancellation, retry lineage, schedule uniqueness, disabled schedules and security boundaries receive automated tests.

## Approval Record

Decision: Accepted through the Product Owner's explicit 2026-09-30 fast-track authorization.

