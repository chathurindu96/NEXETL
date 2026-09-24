# NEXETL Codex Instructions

## Project

This repository contains the implementation workspace for NEXETL,
a next-generation extensible ETL and data integration platform.

## Governing Documentation

Before making architectural or implementation changes, inspect the
applicable documents under `/docs`.

The documents under `/docs` are local development reference copies
of the controlled NEXETL baseline.

The authoritative controlled documentation is maintained in the
NEXETL Google Drive.

Do not modify local documentation as a substitute for the governed
NEXETL change-control process.

## Core Technology Direction

Backend:
Python, Django and Django REST Framework.

Frontend:
Svelte.

Primary metadata database:
PostgreSQL.

API:
REST with OpenAPI 3.1.

Architecture:
Modular monolith unless superseded by an approved architecture
decision.

Deployment direction:
Containerized.

Extensibility:
Connector and extension/plugin architecture.

## Engineering Rules

Do not invent requirements.

Do not silently resolve TBDs.

Do not silently change approved architecture.

Do not introduce architecture-significant technologies merely
because they are common or convenient.

Do not introduce a message broker, workflow engine, scheduler,
cache, alternative database, frontend framework, infrastructure
platform or cloud provider unless supported by the controlled
baseline or an approved decision.

Do not treat logical architecture modules as independently
deployable services unless explicitly approved.

Do not convert the modular monolith into microservices without an
approved architecture decision.

Use object-oriented design where it provides meaningful domain or
architectural value. Do not make everything a class.

Prefer composition and explicit dependencies over deep inheritance
and hidden coupling.

Preserve separation of concerns, high cohesion, low coupling and
dependency inversion at architecture-significant boundaries.

## Backend

Follow the approved backend architecture and software engineering
standards.

Do not equate Django ORM models automatically with domain entities.

Do not create one Django application per database table.

Do not introduce hidden orchestration through Django signals.

Avoid N+1 queries, uncontrolled queries and unnecessarily long
transactions.

Raw SQL requires explicit justification and must be parameterized,
testable and reviewable.

## Frontend

Follow the approved frontend and UX architecture.

Do not invent product screens or workflows during implementation.

Do not replace the governed human-centred UX direction with generic
template-driven SaaS interfaces.

Frontend implementation must follow approved UX/UI detailed design
when applicable.

## Connectors and Extensions

Database and external-system integrations must follow the approved
connector and extension architecture.

Do not hard-code individual database products into the NEXETL core
when the capability belongs behind a connector contract.

Do not create a giant shared BaseConnector hierarchy without
architectural justification.

## Runtime

Long-running ETL execution must not depend on the lifetime of an
HTTP request.

Do not select Celery, Redis, RabbitMQ, Kafka, Airflow, Temporal,
APScheduler, cron or another runtime technology merely because it
is commonly used.

Runtime technology choices must follow approved architecture and
ADRs.

## Security

Never commit passwords, tokens, API keys, certificates or other
secrets.

Never expose server-side secrets to frontend code.

Never log secrets.

Follow the approved NEXETL security architecture.

## Testing

Implementation must follow the approved NEXETL testing and quality
strategy.

A successful execution status alone is not sufficient proof of ETL
correctness.

Test relevant input, transformations, output, types, null handling,
mappings, rejected records, side effects and failure paths.

Integration testing is a first-class requirement.

## Change Control

If an implementation request conflicts with an approved requirement,
architecture document or Accepted ADR:

STOP.

Explain the conflict.

Identify the affected document or decision.

Do not silently work around the architecture.

If an architecture-significant decision is unresolved:

STOP and report it as a decision/TBD requiring governance.

## Implementation Readiness

Do not begin a production implementation increment unless its
applicable requirements, architecture, detailed design, testing
requirements and implementation plan satisfy the governed
implementation-readiness process.

## Important Controlled Documents

Pay particular attention to:

- DOC-023 — Software Engineering and Coding Standards
- DOC-024 — Repository Structure and Development Workflow
- DOC-025 — Testing and Quality Assurance Strategy
- DOC-026 — CI/CD, Release, Versioning and Compatibility Strategy
- DOC-027 — Deployment Architecture
- DOC-028 — Operations, Backup and Disaster Recovery

Also inspect the applicable requirements, architecture documents,
ADRs and detailed designs for the task being implemented.