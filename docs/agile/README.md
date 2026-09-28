# NEXETL Agile Delivery Documentation

This directory translates the approved Increment 1 delivery plan into a reviewable Scrum product backlog. It is planning material, not a replacement for governed requirements, architecture, detailed design, PLAN-001, or Project State.

## Authority and scope

- NEXETL-PLAN-001 v0.1 / Approved supplies the WP-01 through WP-18 delivery backbone.
- NEXETL-DES-001 v1.0 / Approved supplies Increment 1 implementation constraints.
- NEXETL Project State v0.7 / Approved records Gate 5 open for Increment 1.
- REG-002 supplies controlled requirement identifiers.
- ADR-001 through ADR-007 and DOC-023 through DOC-025 remain binding.
- `NEXETL/OLD/` is excluded.

Epics in this directory are planning containers derived from PLAN-001. They do not amend PLAN-001 or authorize work beyond the approved Increment 1 boundary.

## Backlog model

```text
Increment 1 milestone
└── WP Epic
    └── Story / Task / Bug / Spike
        └── Pull request and verification evidence
```

The Product Backlog covers all 18 work packages. Near-term items are refined more deeply than later items. Sprint 1 is a two-week iteration focused on WP-02 and WP-03. Its ten tickets are candidates for commitment until Sprint Planning; no historical velocity is assumed.

## Contents

- [Product Backlog](PRODUCT-BACKLOG.md)
- [Sprint 1](SPRINT-001.md)
- [Ticket Template](TICKET-TEMPLATE.md)
- [Definition of Ready](DEFINITION-OF-READY.md)
- [Definition of Done](DEFINITION-OF-DONE.md)
- [GitHub Project Setup](GITHUB-PROJECT-SETUP.md)
- [Sprint 1 ticket files](tickets/sprint-001/)

## Operating cadence

- Product Backlog refinement clarifies value, sources, dependencies, acceptance criteria, risks, and estimates without prematurely assigning future Sprints.
- Sprint Planning selects a realistic commitment from ready candidates and records any stretch item separately.
- Daily coordination updates status and blockers without creating extra governance layers.
- Sprint Review demonstrates working outcomes and links objective evidence.
- Sprint Retrospective records actionable process improvements; it does not alter governed product or architecture decisions.

## Status rules

- WP-01 is historical and Completed.
- WP-02 and WP-03 are Sprint 1 candidate scope.
- WP-04 through WP-18 remain Product Backlog / Unscheduled.
- A ticket becomes Done only when its acceptance criteria and the applicable Definition of Done are satisfied.
- A material requirement, DES, or architecture contradiction stops affected implementation and returns it to the appropriate governance path.
