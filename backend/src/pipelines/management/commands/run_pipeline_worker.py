"""Run the independently deployable Pipeline worker."""

import socket
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from django.db import close_old_connections

from pipelines.runtime import claim_next_run,execute_run
from pipelines.runtime.queue import recover_expired_runs


class Command(BaseCommand):
    help="Claim and execute queued Pipeline Runs."
    def add_arguments(self,parser):parser.add_argument("--once",action="store_true");parser.add_argument("--concurrency",type=int,default=settings.CONFIGURATION.runtime.worker_concurrency)
    def handle(self,*_,**options):
        concurrency=options["concurrency"]
        if not 1<=concurrency<=8:raise CommandError("concurrency must be from 1 through 8")
        stop=threading.Event();identity=f"{socket.gethostname()}:{uuid.uuid4()}"
        recovered=recover_expired_runs()
        if recovered:self.stdout.write(self.style.WARNING(f"Marked {recovered} abandoned Runs as failed."))
        self.stdout.write(f"Pipeline worker started with concurrency {concurrency}.")
        def loop(slot):
            worker_id=f"{identity}:{slot}"
            while not stop.is_set():
                close_old_connections();run=claim_next_run(worker_id)
                if run:
                    try:execute_run(run.id,worker_id)
                    except Exception:
                        from django.utils import timezone
                        from pipelines.infrastructure.persistence.models import PipelineRunRecord
                        PipelineRunRecord.objects.filter(id=run.id,status__in=["RUNNING","CANCELLING"]).update(status="FAILED",finished_at=timezone.now(),current_node_id=None,error_code="NEXETL_WORKER_FAILURE",error_message="The worker could not complete the Run.")
                elif options["once"]:return
                else:stop.wait(settings.CONFIGURATION.runtime.worker_poll_seconds)
        try:
            with ThreadPoolExecutor(max_workers=concurrency,thread_name_prefix="nexetl-worker") as pool:
                futures=[pool.submit(loop,index) for index in range(concurrency)]
                for future in futures:future.result()
        except KeyboardInterrupt:stop.set();self.stdout.write("Pipeline worker stopping.")
