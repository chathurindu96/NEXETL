"""Database adapter contracts and trusted built-in implementations."""

from __future__ import annotations

import re
import time
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol


Row = dict[str, Any]
Batch = list[Row]


class ConnectorFailure(RuntimeError):
    def __init__(self, code: str, message: str, *, transient: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.public_message = message
        self.transient = transient


class ConnectorAdapter(Protocol):
    key: str
    capabilities: frozenset[str]

    def test_connection(self, configuration: dict[str, object], password: str, timeout: int) -> dict[str, object]: ...
    def discover_schemas(self, configuration: dict[str, object], password: str, timeout: int) -> list[str]: ...
    def discover_datasets(self, configuration: dict[str, object], password: str, schema: str, timeout: int) -> list[dict[str, str]]: ...
    def discover_schema(self, configuration: dict[str, object], password: str, schema: str, dataset: str, timeout: int) -> list[dict[str, object]]: ...
    def read_batches(self, configuration: dict[str, object], password: str, source: dict[str, object], batch_size: int, timeout: int) -> Iterator[Batch]: ...
    def write_batches(self, configuration: dict[str, object], password: str, target: dict[str, object], batches: Iterable[Batch], timeout: int) -> dict[str, int]: ...


def _logical_type(native: str) -> str:
    lowered = native.lower()
    if any(token in lowered for token in ("int", "serial")): return "integer"
    if any(token in lowered for token in ("numeric", "decimal", "real", "double", "money", "float")): return "decimal"
    if "bool" in lowered or lowered == "bit": return "boolean"
    if "timestamp" in lowered or "datetime" in lowered: return "timestamp"
    if lowered == "date": return "date"
    if any(token in lowered for token in ("binary", "bytea", "blob", "image")): return "binary"
    if "json" in lowered: return "json"
    if any(token in lowered for token in ("char", "text", "uuid", "xml")): return "string"
    return "unknown"


def _require_text(configuration: dict[str, object], name: str) -> str:
    value = configuration.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ConnectorFailure("NEXETL_CONNECTION_CONFIGURATION_INVALID", f"Connection field '{name}' is required.")
    return value.strip()


def _port(configuration: dict[str, object], default: int) -> int:
    value = configuration.get("port", default)
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 65535:
        raise ConnectorFailure("NEXETL_CONNECTION_CONFIGURATION_INVALID", "Connection port is invalid.")
    return value


def _safe_query(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConnectorFailure("NEXETL_NODE_CONFIGURATION_INVALID", "A query is required.")
    query = value.strip()
    if ";" in query or not re.match(r"^(select|with)\b", query, re.IGNORECASE):
        raise ConnectorFailure("NEXETL_NODE_CONFIGURATION_INVALID", "Only one read-only SELECT query is supported.")
    return query


def _rows(cursor: Any, size: int) -> Iterator[Batch]:
    columns = [item.name if hasattr(item, "name") else item[0] for item in cursor.description]
    while True:
        values = cursor.fetchmany(size)
        if not values: break
        yield [dict(zip(columns, row, strict=True)) for row in values]


@dataclass(frozen=True)
class PostgreSQLAdapter:
    key: str = "postgresql"
    capabilities: frozenset[str] = frozenset({"test", "discover", "preview", "read", "write", "truncate", "upsert", "transactions"})

    def _connect(self, c: dict[str, object], password: str, timeout: int):
        try:
            import psycopg
            return psycopg.connect(host=_require_text(c, "host"), port=_port(c, 5432), dbname=_require_text(c, "database"), user=_require_text(c, "username"), password=password, connect_timeout=timeout, sslmode=str(c.get("sslMode", "prefer")))
        except ConnectorFailure: raise
        except Exception as error:
            raise ConnectorFailure("NEXETL_CONNECTION_FAILED", "The PostgreSQL Connection could not be opened.", transient=True) from error

    def test_connection(self, c: dict[str, object], password: str, timeout: int) -> dict[str, object]:
        started = time.monotonic()
        with self._connect(c, password, timeout) as connection, connection.cursor() as cursor:
            cursor.execute("select current_database(), version()")
            database, version = cursor.fetchone()
        return {"success": True, "latencyMs": round((time.monotonic() - started) * 1000), "database": database, "server": str(version).split(",")[0]}

    def discover_schemas(self, c, password, timeout):
        with self._connect(c, password, timeout) as connection, connection.cursor() as cursor:
            cursor.execute("select schema_name from information_schema.schemata where schema_name not like 'pg_%' and schema_name <> 'information_schema' order by schema_name")
            return [row[0] for row in cursor.fetchall()]

    def discover_datasets(self, c, password, schema, timeout):
        with self._connect(c, password, timeout) as connection, connection.cursor() as cursor:
            cursor.execute("select table_name, table_type from information_schema.tables where table_schema=%s order by table_name", (schema,))
            return [{"name": row[0], "type": "VIEW" if "VIEW" in row[1] else "TABLE"} for row in cursor.fetchall()]

    def discover_schema(self, c, password, schema, dataset, timeout):
        with self._connect(c, password, timeout) as connection, connection.cursor() as cursor:
            cursor.execute("select column_name, data_type, is_nullable, ordinal_position from information_schema.columns where table_schema=%s and table_name=%s order by ordinal_position", (schema, dataset))
            return [{"name": row[0], "logicalType": _logical_type(row[1]), "nativeType": row[1], "nullable": row[2] == "YES", "ordinal": row[3], "metadata": {}} for row in cursor.fetchall()]

    def read_batches(self, c, password, source, batch_size, timeout):
        from psycopg import sql
        connection = self._connect(c, password, timeout)
        try:
            cursor = connection.cursor(name=f"nexetl_{int(time.time() * 1000)}")
            columns = source.get("columns") or []
            selected = sql.SQL(", ").join(sql.Identifier(str(v)) for v in columns) if columns else sql.SQL("*")
            if source.get("query"):
                cursor.execute(_safe_query(source["query"]))
            else:
                statement = sql.SQL("select {} from {}.{}").format(selected, sql.Identifier(str(source["schema"])), sql.Identifier(str(source["dataset"])))
                cursor.execute(statement)
            yield from _rows(cursor, batch_size)
            cursor.close()
        except ConnectorFailure: raise
        except Exception as error:
            raise ConnectorFailure("NEXETL_SOURCE_READ_FAILED", "The PostgreSQL source could not be read.") from error
        finally:
            connection.close()

    def write_batches(self, c, password, target, batches, timeout):
        from psycopg import sql
        connection = self._connect(c, password, timeout)
        written = 0
        try:
            with connection.cursor() as cursor:
                table = sql.SQL("{}.{}").format(sql.Identifier(str(target["schema"])), sql.Identifier(str(target["table"])))
                if target.get("writeMode") == "TRUNCATE_AND_LOAD": cursor.execute(sql.SQL("truncate table {}").format(table))
                for batch in batches:
                    if not batch: continue
                    columns = list(batch[0])
                    values = [[row.get(column) for column in columns] for row in batch]
                    placeholders = sql.SQL(",").join(sql.Placeholder() for _ in columns)
                    insert = sql.SQL("insert into {} ({}) values ({})").format(table, sql.SQL(",").join(map(sql.Identifier, columns)), placeholders)
                    if target.get("writeMode") == "UPSERT":
                        keys = [str(v) for v in target.get("keyColumns", [])]
                        if not keys: raise ConnectorFailure("NEXETL_NODE_CONFIGURATION_INVALID", "UPSERT requires key columns.")
                        updates = [column for column in columns if column not in keys]
                        insert += sql.SQL(" on conflict ({}) do update set {}").format(sql.SQL(",").join(map(sql.Identifier, keys)), sql.SQL(",").join(sql.SQL("{}=excluded.{}").format(sql.Identifier(column), sql.Identifier(column)) for column in updates))
                    cursor.executemany(insert, values)
                    written += len(batch)
            connection.commit()
            return {"rowsWritten": written}
        except Exception as error:
            connection.rollback()
            if isinstance(error, ConnectorFailure): raise
            raise ConnectorFailure("NEXETL_TARGET_WRITE_FAILED", "The PostgreSQL target write failed.") from error
        finally:
            connection.close()


class MySQLAdapter:
    capabilities = frozenset({"test", "discover", "preview", "read", "write", "truncate", "transactions"})

    def __init__(self, key: str) -> None: self.key = key

    def _connect(self, c, password, timeout):
        try:
            import pymysql
            return pymysql.connect(host=_require_text(c, "host"), port=_port(c, 3306), database=_require_text(c, "database"), user=_require_text(c, "username"), password=password, connect_timeout=timeout, read_timeout=timeout, write_timeout=timeout)
        except ConnectorFailure: raise
        except Exception as error: raise ConnectorFailure("NEXETL_CONNECTION_FAILED", f"The {self.key} Connection could not be opened.", transient=True) from error

    def test_connection(self, c, password, timeout):
        started=time.monotonic()
        with self._connect(c,password,timeout) as connection:
            with connection.cursor() as cursor: cursor.execute("select database(), version()"); database,version=cursor.fetchone()
        return {"success":True,"latencyMs":round((time.monotonic()-started)*1000),"database":database,"server":version}

    def discover_schemas(self,c,password,timeout):
        with self._connect(c,password,timeout) as connection:
            with connection.cursor() as cursor: cursor.execute("select schema_name from information_schema.schemata order by schema_name"); return [row[0] for row in cursor.fetchall()]

    def discover_datasets(self,c,password,schema,timeout):
        with self._connect(c,password,timeout) as connection:
            with connection.cursor() as cursor: cursor.execute("select table_name, table_type from information_schema.tables where table_schema=%s order by table_name",(schema,)); return [{"name":r[0],"type":"VIEW" if "VIEW" in r[1] else "TABLE"} for r in cursor.fetchall()]

    def discover_schema(self,c,password,schema,dataset,timeout):
        with self._connect(c,password,timeout) as connection:
            with connection.cursor() as cursor: cursor.execute("select column_name,data_type,is_nullable,ordinal_position from information_schema.columns where table_schema=%s and table_name=%s order by ordinal_position",(schema,dataset)); return [{"name":r[0],"logicalType":_logical_type(r[1]),"nativeType":r[1],"nullable":r[2]=="YES","ordinal":r[3],"metadata":{}} for r in cursor.fetchall()]

    def read_batches(self,c,password,source,batch_size,timeout):
        connection=self._connect(c,password,timeout)
        try:
            query=_safe_query(source["query"]) if source.get("query") else f"select * from `{str(source['schema']).replace('`','``')}`.`{str(source['dataset']).replace('`','``')}`"
            with connection.cursor() as cursor: cursor.execute(query); yield from _rows(cursor,batch_size)
        except Exception as error: raise ConnectorFailure("NEXETL_SOURCE_READ_FAILED",f"The {self.key} source could not be read.") from error
        finally: connection.close()

    def write_batches(self,c,password,target,batches,timeout):
        if target.get("writeMode") == "UPSERT":
            raise ConnectorFailure(
                "NEXETL_CONNECTOR_CAPABILITY_UNSUPPORTED",
                f"The {self.key} connector does not support UPSERT.",
            )
        connection=self._connect(c,password,timeout); written=0
        try:
            table=f"`{str(target['schema']).replace('`','``')}`.`{str(target['table']).replace('`','``')}`"
            with connection.cursor() as cursor:
                if target.get("writeMode")=="TRUNCATE_AND_LOAD": cursor.execute(f"truncate table {table}")
                for batch in batches:
                    if not batch: continue
                    columns=list(batch[0]); names=",".join(f"`{v.replace('`','``')}`" for v in columns); placeholders=",".join(["%s"]*len(columns))
                    cursor.executemany(f"insert into {table} ({names}) values ({placeholders})",[[row.get(v) for v in columns] for row in batch]); written+=len(batch)
            connection.commit(); return {"rowsWritten":written}
        except Exception as error: connection.rollback(); raise ConnectorFailure("NEXETL_TARGET_WRITE_FAILED",f"The {self.key} target write failed.") from error
        finally: connection.close()


@dataclass(frozen=True)
class SQLServerAdapter:
    key: str = "sqlserver"
    capabilities: frozenset[str] = frozenset({"test", "discover", "preview", "read", "write", "truncate", "transactions"})

    def _connect(self,c,password,timeout):
        try:
            import pyodbc
            driver=str(c.get("driver","ODBC Driver 18 for SQL Server")); encrypt=str(c.get("encrypt","yes")); trust=str(c.get("trustServerCertificate","no"))
            return pyodbc.connect(f"DRIVER={{{driver}}};SERVER={_require_text(c,'host')},{_port(c,1433)};DATABASE={_require_text(c,'database')};UID={_require_text(c,'username')};PWD={password};Encrypt={encrypt};TrustServerCertificate={trust}",timeout=timeout)
        except ConnectorFailure: raise
        except Exception as error: raise ConnectorFailure("NEXETL_CONNECTION_FAILED","The SQL Server Connection could not be opened.",transient=True) from error

    def test_connection(self,c,password,timeout):
        started=time.monotonic(); connection=self._connect(c,password,timeout)
        try: cursor=connection.cursor(); cursor.execute("select db_name(), @@version"); database,version=cursor.fetchone(); return {"success":True,"latencyMs":round((time.monotonic()-started)*1000),"database":database,"server":str(version).splitlines()[0]}
        finally: connection.close()

    def discover_schemas(self,c,password,timeout):
        connection=self._connect(c,password,timeout)
        try: cursor=connection.cursor(); cursor.execute("select schema_name from information_schema.schemata order by schema_name"); return [r[0] for r in cursor.fetchall()]
        finally: connection.close()

    def discover_datasets(self,c,password,schema,timeout):
        connection=self._connect(c,password,timeout)
        try: cursor=connection.cursor(); cursor.execute("select table_name,table_type from information_schema.tables where table_schema=? order by table_name",schema); return [{"name":r[0],"type":"VIEW" if "VIEW" in r[1] else "TABLE"} for r in cursor.fetchall()]
        finally: connection.close()

    def discover_schema(self,c,password,schema,dataset,timeout):
        connection=self._connect(c,password,timeout)
        try: cursor=connection.cursor(); cursor.execute("select column_name,data_type,is_nullable,ordinal_position from information_schema.columns where table_schema=? and table_name=? order by ordinal_position",schema,dataset); return [{"name":r[0],"logicalType":_logical_type(r[1]),"nativeType":r[1],"nullable":r[2]=="YES","ordinal":r[3],"metadata":{}} for r in cursor.fetchall()]
        finally: connection.close()

    def read_batches(self,c,password,source,batch_size,timeout):
        connection=self._connect(c,password,timeout)
        try:
            query=_safe_query(source["query"]) if source.get("query") else f"select * from [{str(source['schema']).replace(']',']]')}].[{str(source['dataset']).replace(']',']]')}]"
            cursor=connection.cursor(); cursor.execute(query); yield from _rows(cursor,batch_size)
        except Exception as error: raise ConnectorFailure("NEXETL_SOURCE_READ_FAILED","The SQL Server source could not be read.") from error
        finally: connection.close()

    def write_batches(self,c,password,target,batches,timeout):
        if target.get("writeMode") == "UPSERT":
            raise ConnectorFailure(
                "NEXETL_CONNECTOR_CAPABILITY_UNSUPPORTED",
                "The SQL Server connector does not support UPSERT.",
            )
        connection=self._connect(c,password,timeout); written=0
        try:
            table=f"[{str(target['schema']).replace(']',']]')}].[{str(target['table']).replace(']',']]')}]"; cursor=connection.cursor()
            if target.get("writeMode")=="TRUNCATE_AND_LOAD": cursor.execute(f"truncate table {table}")
            for batch in batches:
                if not batch: continue
                columns=list(batch[0]); names=",".join(f"[{v.replace(']',']]')}]" for v in columns); placeholders=",".join(["?"]*len(columns)); cursor.fast_executemany=True; cursor.executemany(f"insert into {table} ({names}) values ({placeholders})",[[row.get(v) for v in columns] for row in batch]); written+=len(batch)
            connection.commit(); return {"rowsWritten":written}
        except Exception as error: connection.rollback(); raise ConnectorFailure("NEXETL_TARGET_WRITE_FAILED","The SQL Server target write failed.") from error
        finally: connection.close()


ADAPTERS: dict[str, ConnectorAdapter] = {
    "postgresql": PostgreSQLAdapter(),
    "mysql": MySQLAdapter("mysql"),
    "mariadb": MySQLAdapter("mariadb"),
    "sqlserver": SQLServerAdapter(),
}
