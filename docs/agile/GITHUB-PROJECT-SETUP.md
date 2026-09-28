# GitHub Project Setup — NEXETL Delivery

## Project and hierarchy

Create one GitHub Project named **NEXETL Delivery** after Product Owner approval. Use this hierarchy where GitHub capability permits:

```text
WP Epic issue
└── Story / Task sub-issue
    └── Linked PR and implementation evidence
```

Create one Epic issue for each PLAN-001 work package. Sprint tickets become sub-issues of their governing WP Epic. Do not create issues or change GitHub Projects during this documentation pass.

## Fields

| Field | Type | Values / rule |
| --- | --- | --- |
| Status | Single select | Backlog, Ready, In Progress, In Review, Blocked, Done |
| Sprint | Iteration | Two-week iterations; Iteration represents Sprint |
| Priority | Single select | P0, P1, P2, P3 |
| Story Points | Number | Fibonacci values 1, 2, 3, 5, 8 |
| Work Package | Single select | WP-01 through WP-18 |
| Component | Single select | Backend, Configuration, Database, API, Security, Frontend, Testing, Documentation, DevOps |
| Risk | Single select | Low, Medium, High; review rather than infer Critical |

Use one milestone: **Increment 1 — Pipeline Definition Registration and Inspection Foundation**. The milestone represents the increment/release goal. Do not use milestones to duplicate Sprint iterations.

Priority remains a Project field; do not duplicate it with labels.

## Labels

- `type:epic`
- `type:story`
- `type:task`
- `type:bug`
- `type:spike`
- `component:backend`
- `component:configuration`
- `component:database`
- `component:api`
- `component:security`
- `component:frontend`
- `component:testing`
- `component:documentation`
- `component:devops`

Use `type:spike` only for genuine uncertainty requiring time-boxed investigation. Use technical-debt tickets only for concrete, evidenced debt.

## Views

### Product Backlog

- Layout: table.
- Filter: all open backlog items.
- Group or sort: Priority, then Work Package.

### Current Sprint

- Layout: board.
- Filter: current Sprint iteration.
- Columns: Status.

### Sprint Planning

- Layout: table.
- Filter: current or next-Sprint candidates.
- Show: Priority, Story Points, Work Package, Component, Risk, dependencies.

### Roadmap

- Layout: roadmap.
- Group: Work Package; show iterations only when actually assigned.

### Blocked

- Layout: table.
- Filter: Status = Blocked.
- Show blocker, owner, dependencies, and last update.

### Done

- Layout: table.
- Filter: Status = Done.
- Use for Sprint Review and retrospective evidence.

## Transfer procedure after approval

1. Create the Increment 1 milestone and Project fields.
2. Create WP-01 through WP-18 Epic issues from the Product Backlog.
3. Create approved detailed ticket bodies as child issues.
4. Assign only the Sprint Planning commitment to the active iteration.
5. Keep uncommitted future work in Backlog without an iteration.
6. Link PRs, test output, command evidence, and documentation evidence to the implementing ticket.
7. Close tickets only after the applicable Definition of Done is evidenced.
