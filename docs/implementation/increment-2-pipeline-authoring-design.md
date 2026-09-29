# Increment 2 — Pipeline Authoring Workspace Design

## Authorized scope

This Product Owner-authorized Increment 2 extends the identity-only Increment 1
Pipeline Definition into a design-time authoring workspace. It adds the
Pipeline registry and lifecycle, a read-only connector catalogue, persistent
Pipeline designs, and authenticated SvelteKit Home, Registry, Connector,
Designer, and Settings routes. It does not add execution, schedules, workers,
credentials, connector connectivity, monitoring, tenancy, or runtime state.

## Domain and persistence

`PipelineDefinition` gains name, optional description, `DRAFT`/`ARCHIVED`
lifecycle, and immutable/updated timestamps. Existing IDs are preserved and
backfilled with deterministic `Pipeline <short-id>` names. Django migrations
create normalized `pipeline_design`, `pipeline_design_node`, and
`pipeline_design_edge` tables. Design saves replace nodes/edges atomically and
use an integer revision for optimistic concurrency.

Connector catalogue entries are application-owned reference descriptors rather
than credentials or live connection instances. The initial entries are
PostgreSQL, SQL Server, MySQL, and MariaDB.

## REST and security

All endpoints remain session-authenticated and CSRF-protected for mutations.
Pipeline capabilities are list, register, inspect, update, archive, and design;
superusers use ordinary Django permission evaluation. Registry pagination is
bounded to 20 by default and 100 maximum. Stable errors cover archived edits,
not-found, validation, and stale design revisions.

## Frontend and traceability

Routes are `/home`, `/pipelines`, `/pipelines/new`, `/pipelines/[id]`,
`/pipelines/[id]/design`, `/connectors`, `/connectors/[key]`, and `/settings`.
The existing minimalist shell is retained. The designer uses a compact native
DOM graph workspace with keyboard-operable controls; no runtime behavior or
credential UI exists. Tests cover API/domain/persistence, frontend flows, and
Playwright authoring workflows.
