# NEX-107 Evidence — PostgreSQL Bootstrap Environment Mapping

## Ticket and Work Package

NEX-107 — Configure PostgreSQL Bootstrap Environment Mapping; WP-03.

## Governed Sources

PLAN-001 WP-03/WP-04 boundary; DES-001 §§9, 15.2, 15.4–15.5, 20.1–20.6,
and 21.9; ADR-006; DOC-020; and DOC-024.

## Initial Mapping Inventory

| Concern | Backend variable | Django mapping | Compose mapping | Result |
|---|---|---|---|---|
| Engine | n/a | `django.db.backends.postgresql` | PostgreSQL image | PASS |
| Name/user | `NEXETL_DB_NAME` / `NEXETL_DB_USER` | resolved values | `POSTGRES_DB` / `POSTGRES_USER` | PASS |
| Password | `NEXETL_DB_PASSWORD` | resolved protected value | mandatory `POSTGRES_PASSWORD` | PASS |
| Host | `NEXETL_DB_HOST` | resolved value; local `127.0.0.1` | host-run profile | PASS |
| Published port | `NEXETL_DB_PORT` | resolved integer | `127.0.0.1:${NEXETL_DB_PORT}:5432` | PASS |
| Container port | n/a | n/a | `5432` | PASS |
| Exposure | n/a | n/a | loopback only | PASS |

## Reconciliation Result

No production-source, Compose, example-environment, dependency, or lockfile
defect existed. NEX-107 adds focused evidence, mapping tests, and documentation
only.

## Governed Contract and Topology

`NEXETL_DB_NAME`, `NEXETL_DB_USER`, `NEXETL_DB_PASSWORD`,
`NEXETL_DB_HOST`, and `NEXETL_DB_PORT` are the sole governed database inputs.
Host-run Django connects to `127.0.0.1:NEXETL_DB_PORT`; Compose publishes that
same loopback host port to PostgreSQL container port `5432`. An alternate host
port changes both host-side uses, never the internal port.

## Secret and Driver Safety

The password remains mandatory, externally supplied, and absent from examples,
output, and evidence. `psycopg[binary]` was already present in the manifest and
lock state; no dependency action occurred.

## Verification and Boundary

Focused tests prove PostgreSQL engine selection, default and overridden Django
mapping, typed port mapping, redacted password assertion, and static Compose
loopback/internal-port contract. No PostgreSQL service, connection, SQL,
migration, schema operation, ORM model, session, Pipeline Definition,
authentication/authorization, frontend, NEX-108, or WP-04 work was introduced.

Test results: focused configuration 55 passed; bootstrap 12 passed;
architecture-boundary 4 passed; full backend suite 67 passed; Django system
check passed. `docker compose config --quiet` also passed with a temporary
process-only password and alternate host-port input.

## Database Activity

- PostgreSQL started: NO
- Database connection: NO
- SQL executed: NO
- Migration run: NO
- Schema changed: NO

## Acceptance Criteria Assessment

| Criterion | Result |
|---|---|
| Django settings resolve governed PostgreSQL values | PASS |
| Compose/example/backend mapping is consistent | PASS |
| No live database or schema work is introduced | PASS |

## Follow-Up

WP-04 retains ownership of live PostgreSQL connectivity and persistence work.
