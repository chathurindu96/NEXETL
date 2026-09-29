# Increment 2 Pipeline Authoring Evidence

Increment 2 delivers authenticated, design-time Pipeline authoring only: the
Pipeline Registry, Home, Connector Catalogue, persistent Pipeline Designer,
and Settings. Pipeline metadata and normalized design records are persisted in
PostgreSQL through `pipelines` migrations `0002` through `0004`.

The design schema uses `nexetl_pipeline_design`, `nexetl_pipeline_design_node`,
and `nexetl_pipeline_design_edge`. A design has one current revision; a save
replaces nodes and edges atomically and increments that revision. Stale saves
return `NEXETL_PIPELINE_DESIGN_REVISION_CONFLICT`. Structural validation rejects
invalid edge/node relationships while completeness validation reports missing
sources or targets without mutation.

The browser workspace uses only session-authenticated, CSRF-protected REST
requests. Archived pipelines are inspectable but design mutation is forbidden.
Connector records are catalogue descriptors; no credentials, connection test,
runtime execution, scheduling, run history, monitoring, or data movement is
included.

Run 4 regression coverage includes registry regressions and persistent-design
API tests for empty designs, save/reload, revision conflicts, valid graphs, and
invalid connector structure. The frontend suite, Svelte diagnostics, and
production build are recorded in the command log.
