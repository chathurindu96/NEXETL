"""REST resources for immutable versions, Runs and Schedules."""

from uuid import UUID

from croniter import croniter
from django.db import transaction
from django.db.models import Count,Q
from django.http import HttpRequest
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from nexetl.api.authentication import NexetlSessionAuthentication
from nexetl.api.errors import NexetlAPIError
from pipelines.authorization import require_capability
from pipelines.infrastructure.persistence.models import ConnectionRecord,PipelineDefinitionRecord,PipelineRunRecord,PipelineScheduleRecord,PipelineVersionRecord
from pipelines.runtime.compiler import publish_version
from pipelines.runtime.queue import enqueue_run,request_cancellation
from pipelines.runtime.scheduler import next_occurrence


def _pipeline(value:str)->PipelineDefinitionRecord:
    try:return PipelineDefinitionRecord.objects.get(id=UUID(value))
    except (ValueError,PipelineDefinitionRecord.DoesNotExist) as error:raise NexetlAPIError("NEXETL_PIPELINE_DEFINITION_NOT_FOUND","The Pipeline Definition was not found.",http_status=404,category="not_found") from error


def _run(pipeline:PipelineDefinitionRecord,value:str)->PipelineRunRecord:
    try:return PipelineRunRecord.objects.select_related("version","pipeline","initiated_by").get(id=UUID(value),pipeline=pipeline)
    except (ValueError,PipelineRunRecord.DoesNotExist) as error:raise NexetlAPIError("NEXETL_PIPELINE_RUN_NOT_FOUND","The Pipeline Run was not found.",http_status=404,category="not_found") from error


def _duration(start,finish):return round((finish-start).total_seconds()*1000) if start and finish else None


def version_representation(item:PipelineVersionRecord,detail=False):
    result={"id":str(item.id),"pipelineId":str(item.pipeline_id),"version":item.version,"designRevision":item.design_revision,"createdAt":item.created_at.isoformat(),"createdBy":item.created_by.get_username() if item.created_by else None}
    if detail:result["graph"]=item.snapshot
    return result


def run_representation(item:PipelineRunRecord,detail=False):
    result={"id":str(item.id),"pipelineId":str(item.pipeline_id),"pipelineVersionId":str(item.version_id),"version":item.version.version,"status":item.status,"triggerType":item.trigger_type,"initiatedBy":item.initiated_by.get_username() if item.initiated_by else None,"queuedAt":item.queued_at.isoformat(),"startedAt":item.started_at.isoformat() if item.started_at else None,"finishedAt":item.finished_at.isoformat() if item.finished_at else None,"durationMs":_duration(item.started_at,item.finished_at),"currentNodeId":str(item.current_node_id) if item.current_node_id else None,"cancellationRequested":item.cancellation_requested,"errorCode":item.error_code,"errorMessage":item.error_message,"metrics":item.metrics,"attempt":item.attempt,"parentRunId":str(item.parent_run_id) if item.parent_run_id else None}
    if detail:
        result["graph"]=item.version.snapshot
        result["nodes"]=[{"id":str(node.node_id),"label":node.label,"kind":node.kind,"status":node.status,"startedAt":node.started_at.isoformat() if node.started_at else None,"finishedAt":node.finished_at.isoformat() if node.finished_at else None,"durationMs":_duration(node.started_at,node.finished_at),"inputRows":node.input_rows,"outputRows":node.output_rows,"rejectedRows":node.rejected_rows,"batchCount":node.batch_count,"errorCode":node.error_code,"errorMessage":node.error_message,"metrics":node.metrics} for node in item.node_runs.order_by("started_at","id")]
        result["events"]=[{"id":event.id,"timestamp":event.timestamp.isoformat(),"level":event.level,"event":event.event,"nodeId":str(event.node_id) if event.node_id else None,"message":event.message,"context":event.context} for event in item.events.order_by("id")[:200]]
    return result


def schedule_representation(item:PipelineScheduleRecord):return {"id":str(item.id),"pipelineId":str(item.pipeline_id),"name":item.name,"enabled":item.enabled,"expression":item.expression,"timezone":item.timezone,"nextRunAt":item.next_run_at.isoformat() if item.next_run_at else None,"lastRunAt":item.last_run_at.isoformat() if item.last_run_at else None,"createdAt":item.created_at.isoformat(),"updatedAt":item.updated_at.isoformat()}


class PipelineVersionCollectionView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,pipeline_definition_id):
        require_capability(request,"pipelines.inspect_pipeline_definition");pipeline=_pipeline(pipeline_definition_id);return Response({"items":[version_representation(item) for item in pipeline.versions.select_related("created_by").all()]})
    def post(self,request,pipeline_definition_id):
        require_capability(request,"pipelines.publish_pipeline_version");pipeline=_pipeline(pipeline_definition_id)
        if pipeline.state=="ARCHIVED":raise NexetlAPIError("NEXETL_PIPELINE_ARCHIVED","Archived Pipelines cannot be published.",http_status=409,category="conflict")
        version,result=publish_version(pipeline,request.user)
        if not result.valid:raise NexetlAPIError("NEXETL_PIPELINE_NOT_EXECUTABLE","The Pipeline is not executable.",http_status=422,category="validation",details={"issues":result.issues})
        return Response(version_representation(version,True),status=status.HTTP_201_CREATED)


class PipelineVersionDetailView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,pipeline_definition_id,version_id):
        require_capability(request,"pipelines.inspect_pipeline_definition");pipeline=_pipeline(pipeline_definition_id)
        try:item=PipelineVersionRecord.objects.select_related("created_by").get(id=UUID(version_id),pipeline=pipeline)
        except (ValueError,PipelineVersionRecord.DoesNotExist) as error:raise NexetlAPIError("NEXETL_PIPELINE_VERSION_NOT_FOUND","The Pipeline Version was not found.",http_status=404,category="not_found") from error
        return Response(version_representation(item,True))


class PipelineRunCollectionView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,pipeline_definition_id):
        require_capability(request,"pipelines.inspect_pipeline_run");pipeline=_pipeline(pipeline_definition_id)
        try:page=max(1,int(request.query_params.get("page",1)));page_size=min(100,max(1,int(request.query_params.get("pageSize",20))))
        except ValueError as error:raise ValidationError({"pagination":"Must be integers."}) from error
        query=pipeline.runs.select_related("version","initiated_by").order_by("-queued_at");total=query.count();items=query[(page-1)*page_size:page*page_size]
        return Response({"items":[run_representation(item) for item in items],"page":page,"pageSize":page_size,"totalItems":total,"totalPages":max(1,(total+page_size-1)//page_size)})
    def post(self,request,pipeline_definition_id):
        require_capability(request,"pipelines.run_pipeline_definition");pipeline=_pipeline(pipeline_definition_id)
        if pipeline.state=="ARCHIVED":raise NexetlAPIError("NEXETL_PIPELINE_ARCHIVED","Archived Pipelines cannot be run.",http_status=409,category="conflict")
        idempotency=request.headers.get("Idempotency-Key");run,issues=enqueue_run(pipeline,request.user,idempotency_key=idempotency)
        if not run:raise NexetlAPIError("NEXETL_PIPELINE_NOT_EXECUTABLE","The Pipeline is not executable.",http_status=422,category="validation",details={"issues":issues})
        return Response(run_representation(run),status=status.HTTP_202_ACCEPTED)


class PipelineRunDetailView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,pipeline_definition_id,run_id):require_capability(request,"pipelines.inspect_pipeline_run");return Response(run_representation(_run(_pipeline(pipeline_definition_id),run_id),True))


class PipelineRunCancelView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def post(self,request,pipeline_definition_id,run_id):
        require_capability(request,"pipelines.cancel_pipeline_run");run=_run(_pipeline(pipeline_definition_id),run_id)
        if run.status in {"SUCCEEDED","FAILED","CANCELLED"}:raise NexetlAPIError("NEXETL_PIPELINE_RUN_ALREADY_FINISHED","The Pipeline Run has already finished.",http_status=409,category="conflict")
        return Response(run_representation(request_cancellation(run)))


class PipelineRunRetryView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def post(self,request,pipeline_definition_id,run_id):
        require_capability(request,"pipelines.run_pipeline_definition");pipeline=_pipeline(pipeline_definition_id);previous=_run(pipeline,run_id)
        if previous.status not in {"FAILED","CANCELLED"}:raise NexetlAPIError("NEXETL_PIPELINE_RUN_RETRY_INVALID","Only failed or cancelled Runs can be retried.",http_status=409,category="conflict")
        run,_=enqueue_run(pipeline,request.user,trigger_type="RETRY",version=previous.version,parent_run=previous,idempotency_key=request.headers.get("Idempotency-Key"));return Response(run_representation(run),status=202)


class PipelineScheduleCollectionView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request,pipeline_definition_id):require_capability(request,"pipelines.inspect_pipeline_run");return Response({"items":[schedule_representation(item) for item in _pipeline(pipeline_definition_id).schedules.order_by("name")]})
    def post(self,request,pipeline_definition_id):
        require_capability(request,"pipelines.manage_pipeline_schedule");pipeline=_pipeline(pipeline_definition_id);payload=request.data if isinstance(request.data,dict) else {};name=payload.get("name");expression=payload.get("expression");timezone_name=payload.get("timezone","UTC")
        if not isinstance(name,str) or not name.strip():raise ValidationError({"name":"Required."})
        try:
            if not isinstance(expression,str) or not croniter.is_valid(expression):raise ValueError()
            next_run=next_occurrence(expression,str(timezone_name))
        except Exception as error:raise ValidationError({"expression":"A valid cron expression and timezone are required."}) from error
        item=PipelineScheduleRecord.objects.create(pipeline=pipeline,name=name.strip(),enabled=bool(payload.get("enabled",True)),expression=expression,timezone=str(timezone_name),next_run_at=next_run,created_by=request.user);return Response(schedule_representation(item),status=201)


class PipelineScheduleDetailView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def patch(self,request,pipeline_definition_id,schedule_id):
        require_capability(request,"pipelines.manage_pipeline_schedule");pipeline=_pipeline(pipeline_definition_id)
        try:item=PipelineScheduleRecord.objects.get(id=UUID(schedule_id),pipeline=pipeline)
        except (ValueError,PipelineScheduleRecord.DoesNotExist) as error:raise NexetlAPIError("NEXETL_PIPELINE_SCHEDULE_NOT_FOUND","The Pipeline Schedule was not found.",http_status=404,category="not_found") from error
        payload=request.data if isinstance(request.data,dict) else {};item.name=str(payload.get("name",item.name)).strip();item.enabled=bool(payload.get("enabled",item.enabled));item.expression=str(payload.get("expression",item.expression));item.timezone=str(payload.get("timezone",item.timezone))
        try:item.next_run_at=next_occurrence(item.expression,item.timezone) if item.enabled else None
        except Exception as error:raise ValidationError({"expression":"A valid cron expression and timezone are required."}) from error
        item.save();return Response(schedule_representation(item))


class OperationsSummaryView(APIView):
    authentication_classes=[NexetlSessionAuthentication]
    def get(self,request):
        require_capability(request,"pipelines.inspect_pipeline_run");today=timezone.now().date();counts=PipelineRunRecord.objects.aggregate(running=Count("id",filter=Q(status__in=["RUNNING","CANCELLING"])),failed=Count("id",filter=Q(status="FAILED")),today=Count("id",filter=Q(queued_at__date=today)));recent=PipelineRunRecord.objects.select_related("pipeline","version","initiated_by").order_by("-queued_at")[:8]
        return Response({"runningNow":counts["running"],"failedRuns":counts["failed"],"runsToday":counts["today"],"scheduledPipelines":PipelineScheduleRecord.objects.filter(enabled=True).values("pipeline_id").distinct().count(),"availableConnections":ConnectionRecord.objects.filter(state="ENABLED").count(),"recentRuns":[{**run_representation(item),"pipelineName":item.pipeline.name} for item in recent]})
