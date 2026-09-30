"""Real PostgreSQL adapter acceptance for source, join, and target writes."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from django.db import connection

from pipelines.connections.adapters import PostgreSQLAdapter
from pipelines.runtime.executors import ExecutionContext,execute_node
from pipelines.runtime.spool import SpoolStore


def _profile():
    values=connection.settings_dict
    return {"host":values["HOST"] or "127.0.0.1","port":int(values["PORT"] or 5432),"database":values["NAME"],"username":values["USER"],"sslMode":"prefer"},values["PASSWORD"]


@pytest.mark.django_db(transaction=True)
def test_real_postgresql_source_to_target_and_multi_source_join():
    suffix=uuid4().hex[:10];source=f"nexetl_accept_source_{suffix}";lookup=f"nexetl_accept_lookup_{suffix}";target=f"nexetl_accept_target_{suffix}";joined_target=f"nexetl_accept_joined_{suffix}"
    with connection.cursor() as cursor:
        cursor.execute(f'create table "{source}" (id integer primary key, amount numeric(10,2))');cursor.execute(f'create table "{lookup}" (id integer primary key, region text)');cursor.execute(f'create table "{target}" (id integer, amount numeric(10,2))');cursor.execute(f'create table "{joined_target}" (id integer, amount numeric(10,2), right_id integer, region text)');cursor.execute(f'insert into "{source}" values (1,10.50),(2,20.00)');cursor.execute(f"insert into \"{lookup}\" values (1,'East'),(3,'West')")
    adapter=PostgreSQLAdapter();profile,password=_profile()
    try:
        batches=list(adapter.read_batches(profile,password,{"schema":"public","dataset":source},1,10));assert sum(map(len,batches))==2
        result=adapter.write_batches(profile,password,{"schema":"public","table":target,"writeMode":"APPEND"},batches,10);assert result=={"rowsWritten":2}
        with connection.cursor() as cursor:cursor.execute(f'select id,amount from "{target}" order by id');assert [(row[0],float(row[1])) for row in cursor.fetchall()]==[(1,10.5),(2,20.0)]
        right=[row for batch in adapter.read_batches(profile,password,{"schema":"public","dataset":lookup},100,10) for row in batch]
        with SpoolStore(100,1000) as spool:
            spool.write("left",[row for batch in batches for row in batch]);spool.write("right",right);node=SimpleNamespace(design_node_id=uuid4(),kind="join",configuration={"joinType":"FULL","keys":[{"left":"id","right":"id"}]});metrics=execute_node(node,ExecutionContext(spool,{"left":[("left","output")],"right":[("right","output")]},lambda:False,lambda *_:None));joined=spool.all(str(node.design_node_id));assert metrics["outputRows"]==3
            adapter.write_batches(profile,password,{"schema":"public","table":joined_target,"writeMode":"APPEND"},[joined],10)
        with connection.cursor() as cursor:cursor.execute(f'select count(*) from "{joined_target}"');assert cursor.fetchone()[0]==3
    finally:
        with connection.cursor() as cursor:
            for table in (joined_target,target,lookup,source):cursor.execute(f'drop table if exists "{table}"')
