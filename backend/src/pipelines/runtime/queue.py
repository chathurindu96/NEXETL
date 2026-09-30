"""Transactional PostgreSQL-backed Run queue operations."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from pipelines.infrastructure.persistence.models import PipelineDefinitionRecord, PipelineRunRecord, PipelineVersionRecord
from pipelines.runtime.compiler import publish_version


@transaction.atomic
def enqueue_run(pipeline: PipelineDefinitionRecord, user, *, trigger_type: str = "MANUAL", idempotency_key: str | None = None, version: PipelineVersionRecord | None = None, parent_run: PipelineRunRecord | None = None, schedule=None, scheduled_for=None):
    if idempotency_key:
        existing=PipelineRunRecord.objects.filter(pipeline=pipeline,idempotency_key=idempotency_key).first()
        if existing: return existing,[]
    issues=[]
    if version is None:
        version,result=publish_version(pipeline,user); issues=result.issues
        if not result.valid: return None,issues
    run=PipelineRunRecord.objects.create(pipeline=pipeline,version=version,trigger_type=trigger_type,initiated_by=user if getattr(user,"is_authenticated",False) else None,idempotency_key=idempotency_key,parent_run=parent_run,schedule=schedule,scheduled_for=scheduled_for,attempt=(parent_run.attempt+1 if parent_run else 1))
    return run,issues


@transaction.atomic
def claim_next_run(worker_id: str) -> PipelineRunRecord | None:
    now=timezone.now(); run=PipelineRunRecord.objects.select_for_update(skip_locked=True).filter(status="QUEUED").order_by("queued_at").first()
    if run is None: return None
    run.status="RUNNING"; run.claimed_by=worker_id; run.claimed_at=now; run.started_at=now; run.heartbeat_at=now; run.lease_expires_at=now+timedelta(seconds=settings.CONFIGURATION.runtime.worker_lease_seconds)
    run.save(update_fields=["status","claimed_by","claimed_at","started_at","heartbeat_at","lease_expires_at"])
    return run


def request_cancellation(run: PipelineRunRecord) -> PipelineRunRecord:
    if run.status in {"SUCCEEDED","FAILED","CANCELLED"}: return run
    run.cancellation_requested=True
    if run.status=="RUNNING": run.status="CANCELLING"
    elif run.status=="QUEUED": run.status="CANCELLED"; run.finished_at=timezone.now()
    run.save(update_fields=["cancellation_requested","status","finished_at"])
    return run


def heartbeat(run_id: UUID) -> None:
    now=timezone.now(); PipelineRunRecord.objects.filter(id=run_id,status__in=["RUNNING","CANCELLING"]).update(heartbeat_at=now,lease_expires_at=now+timedelta(seconds=settings.CONFIGURATION.runtime.worker_lease_seconds))


@transaction.atomic
def recover_expired_runs() -> int:
    """Fail abandoned claimed Runs without risking duplicate target writes."""
    now=timezone.now()
    expired=PipelineRunRecord.objects.select_for_update(skip_locked=True).filter(status__in=["RUNNING","CANCELLING"],lease_expires_at__lt=now)
    count=expired.count()
    expired.update(status="FAILED",finished_at=now,current_node_id=None,error_code="NEXETL_WORKER_LEASE_EXPIRED",error_message="The worker stopped before the Run completed.")
    return count
