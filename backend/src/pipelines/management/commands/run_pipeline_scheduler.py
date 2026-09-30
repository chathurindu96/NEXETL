"""Run the independently deployable Pipeline scheduler."""

import time

from django.core.management.base import BaseCommand

from pipelines.runtime.scheduler import enqueue_due_schedules


class Command(BaseCommand):
    help="Enqueue due Pipeline schedules."
    def add_arguments(self,parser):parser.add_argument("--once",action="store_true");parser.add_argument("--interval",type=int,default=30)
    def handle(self,*_,**options):
        self.stdout.write("Pipeline scheduler started.")
        try:
            while True:
                count=enqueue_due_schedules();
                if count:self.stdout.write(f"Enqueued {count} scheduled Pipeline Run(s).")
                if options["once"]:break
                time.sleep(max(1,min(options["interval"],60)))
        except KeyboardInterrupt:self.stdout.write("Pipeline scheduler stopping.")
