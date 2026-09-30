"""Durable schedule evaluation with row locking and occurrence uniqueness."""

from datetime import datetime
from zoneinfo import ZoneInfo

from croniter import croniter
from django.db import transaction
from django.utils import timezone

from pipelines.infrastructure.persistence.models import PipelineScheduleRecord
from pipelines.runtime.queue import enqueue_run


def next_occurrence(expression:str,timezone_name:str,base:datetime|None=None)->datetime:
    zone=ZoneInfo(timezone_name); current=(base or timezone.now()).astimezone(zone); return croniter(expression,current,max_years_between_matches=2).get_next(datetime).astimezone(ZoneInfo("UTC"))


@transaction.atomic
def enqueue_due_schedules(now:datetime|None=None)->int:
    current=now or timezone.now(); schedules=PipelineScheduleRecord.objects.select_for_update(skip_locked=True,of=("self",)).select_related("pipeline","created_by").filter(enabled=True,next_run_at__lte=current).order_by("next_run_at"); count=0
    for schedule in schedules:
        occurrence=schedule.next_run_at
        run,_=enqueue_run(schedule.pipeline,schedule.created_by,trigger_type="SCHEDULED",idempotency_key=f"schedule:{schedule.id}:{occurrence.isoformat()}",schedule=schedule,scheduled_for=occurrence)
        if run:count+=1;schedule.last_run_at=occurrence
        schedule.next_run_at=next_occurrence(schedule.expression,schedule.timezone,occurrence);schedule.save(update_fields=["last_run_at","next_run_at","updated_at"])
    return count
