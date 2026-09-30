"""Run coordinator: lifecycle, node execution, metrics and safe failures."""

from __future__ import annotations

import logging
import time
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from pipelines.connections import ConnectorFailure
from pipelines.infrastructure.persistence.models import PipelineNodeRunRecord, PipelineRunEventRecord, PipelineRunRecord
from pipelines.runtime.compiler import compile_snapshot
from pipelines.runtime.executors import ExecutionContext, execute_node
from pipelines.runtime.queue import heartbeat
from pipelines.runtime.spool import SpoolStore


logger=logging.getLogger("pipelines.runtime")


def _event(run:PipelineRunRecord,event:str,message:str,*,node_id=None,level="INFO",context=None):
    PipelineRunEventRecord.objects.create(run=run,node_id=node_id,event=event,message=message,level=level,context=context or {})
    logger.log(getattr(logging,level,logging.INFO),"event=%s run_id=%s pipeline_id=%s version_id=%s node_id=%s",event,run.id,run.pipeline_id,run.version_id,node_id)


def _safe_error(error:Exception)->tuple[str,str]:
    if isinstance(error,ConnectorFailure):return error.code,error.public_message
    text=str(error)
    if text.startswith("NEXETL_"):return text,"The node could not complete its configured operation."
    return "NEXETL_NODE_EXECUTION_FAILED","The node failed during execution."


def execute_run(run_id:UUID,worker_id:str)->PipelineRunRecord:
    run=PipelineRunRecord.objects.select_related("version","pipeline").get(id=run_id)
    if run.status not in {"RUNNING","CANCELLING"} or run.claimed_by!=worker_id:return run
    result=compile_snapshot(run.version.snapshot)
    if not result.valid:
        run.status="FAILED";run.error_code="NEXETL_PIPELINE_NOT_EXECUTABLE";run.error_message="The immutable Pipeline Version did not pass execution validation.";run.finished_at=timezone.now();run.save(update_fields=["status","error_code","error_message","finished_at"]);_event(run,"run_failed",run.error_message,level="ERROR",context={"issues":result.issues});return run
    version_nodes={str(node.design_node_id):node for node in run.version.nodes.all()}; edges=list(run.version.edges.all()); incoming={node_id:{} for node_id in version_nodes}
    for edge in edges:incoming[str(edge.target_node_id)].setdefault(edge.target_port,[]).append((str(edge.source_node_id),edge.source_port))
    for node_id in result.order:
        node=version_nodes[node_id];PipelineNodeRunRecord.objects.get_or_create(run=run,node_id=node.design_node_id,defaults={"label":node.label,"kind":node.kind})
    _event(run,"run_started","Pipeline Run started.")
    failed=False;cancelled=False;totals={"rowsRead":0,"rowsWritten":0,"rowsRejected":0,"batchCount":0}
    with SpoolStore(settings.CONFIGURATION.runtime.batch_size,settings.CONFIGURATION.runtime.stateful_max_rows) as spool:
        for node_id in result.order:
            node=version_nodes[node_id];node_run=PipelineNodeRunRecord.objects.get(run=run,node_id=node.design_node_id)
            if failed or cancelled:
                node_run.status="SKIPPED";node_run.finished_at=timezone.now();node_run.save(update_fields=["status","finished_at"]);continue
            run.refresh_from_db(fields=["cancellation_requested","status"])
            if run.cancellation_requested:cancelled=True;node_run.status="CANCELLED";node_run.finished_at=timezone.now();node_run.save(update_fields=["status","finished_at"]);continue
            started=time.monotonic();node_run.status="RUNNING";node_run.started_at=timezone.now();node_run.save(update_fields=["status","started_at"]);run.current_node_id=node.design_node_id;run.save(update_fields=["current_node_id"]);_event(run,"node_started",f"{node.label} started.",node_id=node.design_node_id);heartbeat(run.id)
            context=ExecutionContext(spool,incoming[node_id],lambda:PipelineRunRecord.objects.filter(id=run.id,cancellation_requested=True).exists(),lambda code,message:_event(run,"node_warning",message,node_id=node.design_node_id,level="WARNING",context={"code":code}))
            try:
                metrics=execute_node(node,context);duration=round((time.monotonic()-started)*1000);metrics["durationMs"]=duration;node_run.status="SUCCEEDED";node_run.finished_at=timezone.now();node_run.input_rows=metrics.get("inputRows",0);node_run.output_rows=metrics.get("outputRows",0);node_run.rejected_rows=metrics.get("rejectedRows",0);node_run.batch_count=metrics.get("batchCount",0);node_run.metrics=metrics;node_run.save();totals["rowsRead"]+=node_run.input_rows;totals["rowsWritten"]+=node_run.output_rows;totals["rowsRejected"]+=node_run.rejected_rows;totals["batchCount"]+=node_run.batch_count;_event(run,"node_completed",f"{node.label} completed.",node_id=node.design_node_id,context=metrics)
            except InterruptedError:
                cancelled=True;node_run.status="CANCELLED";node_run.finished_at=timezone.now();node_run.error_code="NEXETL_PIPELINE_RUN_CANCELLED";node_run.error_message="Cancellation was requested.";node_run.save();_event(run,"node_cancelled",f"{node.label} stopped at a safe boundary.",node_id=node.design_node_id,level="WARNING")
            except Exception as error:
                failed=True;code,message=_safe_error(error);node_run.status="FAILED";node_run.finished_at=timezone.now();node_run.error_code=code;node_run.error_message=message;node_run.save();run.error_code=code;run.error_message=message;_event(run,"node_failed",message,node_id=node.design_node_id,level="ERROR",context={"code":code});logger.error("Pipeline node execution failed run_id=%s node_id=%s code=%s",run.id,node.design_node_id,code)
    run.finished_at=timezone.now();run.current_node_id=None;run.metrics=totals
    if cancelled:run.status="CANCELLED";run.error_code="NEXETL_PIPELINE_RUN_CANCELLED";run.error_message="The Run was cancelled.";event="run_cancelled"
    elif failed:run.status="FAILED";event="run_failed"
    else:run.status="SUCCEEDED";event="run_completed"
    run.save(update_fields=["status","finished_at","current_node_id","metrics","error_code","error_message"]);_event(run,event,f"Pipeline Run {run.status.lower()}.",level="ERROR" if failed else "INFO",context=totals);return run
