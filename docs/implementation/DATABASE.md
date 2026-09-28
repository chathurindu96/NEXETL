# Backend Foundation Database Operations

This slice configures Django for the existing WP-01 PostgreSQL service. It does not create application-domain tables or run migrations.

## Local connection profile

| Concern | Value/source | Classification |
|---|---|---|
| Database engine | PostgreSQL through Django's PostgreSQL backend | Non-secret |
| Database name | `NEXETL_DB_NAME`, local default `nexetl` | Non-secret |
| Application database user | `NEXETL_DB_USER`, local default `nexetl` | Non-secret |
| Password | `NEXETL_DB_PASSWORD`, required with no default | Secret |
| Host | `NEXETL_DB_HOST`, local default `127.0.0.1` | Non-secret |
| Port | `NEXETL_DB_PORT`, local default `5432`, resolved as an integer | Non-secret |

The existing Compose service maps PostgreSQL to loopback only. Django receives
resolved values through the process environment and the centralized
`nexetl.configuration` boundary; it does not load `.env` files. NEX-105 only
resolves database configuration. It does not start PostgreSQL, connect to it,
execute SQL, run migrations, or change schema.

## Validate the Compose definition

Working directory: `C:\Projects\NEXETL`

```cmd
set NEXETL_DB_PASSWORD=YOUR_PRIVATE_LOCAL_DATABASE_PASSWORD
docker compose config --quiet
```

Expected result: exit code 0.

## Start PostgreSQL

Working directory: `C:\Projects\NEXETL`

```cmd
docker compose up -d postgres
docker compose ps
```

Expected result: `postgres` is running and bound to `127.0.0.1:5432` unless the governed local port variable is explicitly changed.

## Open psql in the PostgreSQL container

Working directory: `C:\Projects\NEXETL`

```cmd
docker compose exec postgres psql -U nexetl -d nexetl
```

If local non-secret database/user values were changed, substitute their resolved values.

## Read-only inspection queries

Check the current database:

```sql
SELECT current_database();
```

Check the current database user:

```sql
SELECT current_user;
```

Check the PostgreSQL version:

```sql
SELECT version();
```

Verify that the connected database exists:

```sql
SELECT datname
FROM pg_database
WHERE datname = current_database();
```

Verify that the connected role exists:

```sql
SELECT rolname
FROM pg_roles
WHERE rolname = current_user;
```

Equivalent one-command examples:

```cmd
docker compose exec postgres psql -U nexetl -d nexetl -c "SELECT current_database();"
docker compose exec postgres psql -U nexetl -d nexetl -c "SELECT current_user;"
docker compose exec postgres psql -U nexetl -d nexetl -c "SELECT version();"
```

## Verify connectivity through Django

Working directory: `C:\Projects\NEXETL\backend`

```cmd
uv run python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor)"
```

Expected output: `postgresql`.

This opens a framework-managed connection only. It does not create a domain table.

## Schema ownership rule

Application schema must be created through governed Django migrations, not ad-hoc manual DDL.

The future `nexetl_pipeline_definition` table belongs to the later authorized Django model/migration slice. It is not created, proposed as manual DDL, or migrated here.

## Commands and queries executed in this slice

Executed database-side/tooling commands:

- `docker --version` — Docker client 28.5.1 was available.
- `docker info --format {{.ServerVersion}}` — failed because the Docker daemon was not running.
- `docker compose config --quiet` with a temporary non-secret check password — passed.
- `docker compose ps` — failed because the Docker daemon was not running.

Executed SQL queries: **None**.

Because the daemon was unavailable, PostgreSQL was not started and the documented SELECT queries and Django connectivity command were not executed. Runtime connectivity remains blocked only by current local Docker state; no competing database configuration was introduced.
