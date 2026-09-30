"""Focused tests for the executable Pipeline platform boundaries."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from pipelines.connections import ConnectorFailure, LocalEncryptedSecretProvider
from pipelines.connections.adapters import MySQLAdapter, SQLServerAdapter
from pipelines.infrastructure.persistence.models import ConnectionSecretRecord,PipelineDefinitionRecord,PipelineRunRecord,PipelineScheduleRecord,PipelineVersionRecord
from pipelines.node_registry import NODE_TYPE_BY_KEY,NODE_TYPES
from pipelines.runtime.compiler import compile_snapshot
from pipelines.runtime.expressions import ExpressionError,evaluate,predicate
from pipelines.runtime.queue import claim_next_run,recover_expired_runs,request_cancellation
from pipelines.runtime.scheduler import enqueue_due_schedules,next_occurrence
from pipelines.runtime.spool import SpoolStore
from pipelines.schema import infer_schema,schema_issues


@pytest.mark.parametrize(("expression","expected"),[("upper(name)","ADA"),("lower(name)","ada"),("trim(' x ')","x"),("concat(name, '-', code)","Ada-7"),("amount * 2 + 1",9),("coalesce(missing, name)","Ada")])
def test_safe_expression_functions(expression,expected):assert evaluate(expression,{"name":"Ada","code":7,"amount":4})==expected


def test_expression_rejects_arbitrary_python():
    with pytest.raises(ExpressionError):evaluate("__import__('os').system('whoami')",{})


@pytest.mark.parametrize(("rule","expected"),[({"column":"age","operator":">=","value":18},True),({"column":"name","operator":"contains","value":"d"},True),({"column":"name","operator":"starts with","value":"A"},True),({"column":"missing","operator":"is null"},True),({"logic":"AND","conditions":[{"column":"age","operator":">","value":10},{"column":"name","operator":"=","value":"Ada"}]},True)])
def test_structured_predicates(rule,expected):assert predicate(rule,{"age":21,"name":"Ada"}) is expected


def test_registry_exposes_required_production_families():
    assert len(NODE_TYPES)>=19
    assert {"database_source","sql_query_source","join","union","split_router","data_quality","database_target"}<=set(NODE_TYPE_BY_KEY)
    assert {port.key for port in NODE_TYPE_BY_KEY["join"].inputs}=={"left","right"}


@pytest.mark.parametrize(
    "adapter",
    [MySQLAdapter("mysql"), MySQLAdapter("mariadb"), SQLServerAdapter()],
)
def test_connectors_reject_unsupported_upsert_before_connecting(adapter):
    with pytest.raises(ConnectorFailure, match="does not support UPSERT"):
        adapter.write_batches({}, "unused", {"writeMode": "UPSERT"}, [], 1)


def test_schema_propagates_select_rename_cast_aggregate_and_join():
    source=[{"name":"id","logicalType":"string","nullable":False,"ordinal":1},{"name":"amount","logicalType":"decimal","nullable":True,"ordinal":2}]
    selected=infer_schema("select_columns",{"columns":["amount","id"]},{"input":[source]});assert [f["name"] for f in selected]==["amount","id"]
    renamed=infer_schema("rename_columns",{"mappings":[{"from":"id","to":"customer_id"}]},{"input":[source]});assert renamed[0]["name"]=="customer_id"
    cast=infer_schema("cast",{"casts":[{"column":"id","type":"integer"}]},{"input":[source]});assert cast[0]["logicalType"]=="integer"
    aggregate=infer_schema("aggregate",{"groupBy":["id"],"aggregates":[{"function":"SUM","column":"amount","as":"total"}]},{"input":[source]});assert [f["name"] for f in aggregate]==["id","total"]
    joined=infer_schema("join",{}, {"left":[source],"right":[source]});assert [f["name"] for f in joined]==["id","amount","right_id","right_amount"]


def test_union_schema_mismatch_is_actionable():
    first=[{"name":"id","logicalType":"integer","nullable":False,"ordinal":1}];second=[{"name":"id","logicalType":"string","nullable":False,"ordinal":1}]
    assert schema_issues("union",{}, {"input":[first,second]},first)[0]["code"]=="NEXETL_SCHEMA_UNION_MISMATCH"


def test_compiler_detects_cycles_required_inputs_and_dynamic_routes():
    left,right,join,router,target=map(str,[uuid4(),uuid4(),uuid4(),uuid4(),uuid4()])
    nodes=[{"id":left,"kind":"database_source","configuration":{"connectionId":"x","schema":"public","dataset":"a"}},{"id":right,"kind":"database_source","configuration":{"connectionId":"x","schema":"public","dataset":"b"}},{"id":join,"kind":"join","configuration":{"joinType":"INNER","keys":[{"left":"id","right":"id"}]}},{"id":router,"kind":"split_router","configuration":{"routes":[{"key":"valid","predicate":{"column":"id","operator":"is not null"}}]}},{"id":target,"kind":"database_target","configuration":{"connectionId":"x","schema":"public","table":"out","writeMode":"APPEND"}}]
    edges=[{"sourceNodeId":left,"sourcePort":"output","targetNodeId":join,"targetPort":"left"},{"sourceNodeId":right,"sourcePort":"output","targetNodeId":join,"targetPort":"right"},{"sourceNodeId":join,"sourcePort":"output","targetNodeId":router,"targetPort":"input"},{"sourceNodeId":router,"sourcePort":"valid","targetNodeId":target,"targetPort":"input"}]
    assert compile_snapshot({"nodes":nodes,"edges":edges}).valid
    missing=compile_snapshot({"nodes":nodes,"edges":edges[1:]});assert any(i["code"]=="NEXETL_INPUT_REQUIRED" for i in missing.issues)
    cycle=compile_snapshot({"nodes":nodes,"edges":[*edges,{"sourceNodeId":router,"sourcePort":"valid","targetNodeId":join,"targetPort":"left"}]});assert any(i["code"]=="NEXETL_DESIGN_CYCLE" for i in cycle.issues)


def test_spool_batches_bounds_and_cleans_up():
    store=SpoolStore(2,3);path=store.path
    store.write("a",[{"id":1},{"id":2},{"id":3}]);assert [len(v) for v in store.batches("a")]==[2,1]
    with pytest.raises(RuntimeError,match="NEXETL_STATEFUL_ROW_LIMIT"):store.write("a",[{"id":4}])
    store.close();assert not path.exists()


def test_timezone_schedule_is_bounded():
    result=next_occurrence("0 2 * * *","Asia/Singapore")
    assert timezone.now()<result<timezone.now()+timedelta(days=2)


@pytest.mark.django_db(transaction=True)
def test_due_schedule_locks_only_schedule_rows_and_enqueues_once():
    pipeline=PipelineDefinitionRecord.objects.create(id=uuid4(),name="Scheduled")
    PipelineVersionRecord.objects.create(pipeline=pipeline,version=1,design_revision=1,snapshot={"nodes":[],"edges":[]},snapshot_hash="b"*64)
    due=timezone.now()-timedelta(minutes=1);schedule=PipelineScheduleRecord.objects.create(pipeline=pipeline,name="Every hour",expression="0 * * * *",timezone="UTC",next_run_at=due)
    assert enqueue_due_schedules()==1
    schedule.refresh_from_db();assert schedule.last_run_at==due and schedule.next_run_at>due
    assert PipelineRunRecord.objects.filter(schedule=schedule,scheduled_for=due,trigger_type="SCHEDULED").count()==1


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_local_secret_is_encrypted_replaceable_and_resolvable():
    provider=LocalEncryptedSecretProvider();reference=provider.store("private-value");record=ConnectionSecretRecord.objects.get(id=reference)
    assert "private-value" not in record.encrypted_value and provider.resolve(reference)=="private-value"
    provider.replace(reference,"replacement");assert provider.resolve(reference)=="replacement"


def _client():
    user=get_user_model().objects.create_user(username=f"runtime-{uuid4()}",password="test-password")
    user.user_permissions.add(*Permission.objects.filter(content_type__app_label="pipelines"))
    client=APIClient(enforce_csrf_checks=True);assert client.login(username=user.username,password="test-password");client.get("/api/security/csrf/");return client,client.cookies["csrftoken"].value


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_connection_api_never_returns_password():
    client,csrf=_client();payload={"name":"Warehouse","connectorKey":"postgresql","description":"Test","configuration":{"host":"localhost","port":5432,"database":"nexetl","username":"etl","sslMode":"prefer"},"password":"write-only-secret"}
    created=client.post("/api/connections/",payload,format="json",HTTP_X_CSRFTOKEN=csrf);assert created.status_code==201
    body=created.json();assert body["secretConfigured"] is True and "password" not in str(body) and "write-only-secret" not in str(body)
    fetched=client.get(f"/api/connections/{body['id']}/").json();assert "write-only-secret" not in str(fetched)


@pytest.mark.django_db
def test_connection_api_rejects_secrets_in_metadata():
    client,csrf=_client();response=client.post("/api/connections/",{"name":"Bad","connectorKey":"postgresql","configuration":{"password":"leak"},"password":"safe-channel"},format="json",HTTP_X_CSRFTOKEN=csrf)
    assert response.status_code==400 and "Secrets must use" in str(response.json())


@pytest.mark.django_db(transaction=True)
def test_queue_claim_cancel_and_lease_recovery():
    pipeline=PipelineDefinitionRecord.objects.create(id=uuid4(),name="Queue")
    version=PipelineVersionRecord.objects.create(pipeline=pipeline,version=1,design_revision=1,snapshot={"nodes":[],"edges":[]},snapshot_hash="a"*64)
    queued=PipelineRunRecord.objects.create(pipeline=pipeline,version=version);claimed=claim_next_run("worker-1");assert claimed.id==queued.id and claimed.status=="RUNNING"
    claimed.lease_expires_at=timezone.now()-timedelta(seconds=1);claimed.save(update_fields=["lease_expires_at"]);assert recover_expired_runs()==1;claimed.refresh_from_db();assert claimed.status=="FAILED" and claimed.error_code=="NEXETL_WORKER_LEASE_EXPIRED"
    another=PipelineRunRecord.objects.create(pipeline=pipeline,version=version);request_cancellation(another);another.refresh_from_db();assert another.status=="CANCELLED"
