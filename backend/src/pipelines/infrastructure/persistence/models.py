"""Physical PostgreSQL representation of Pipeline design and runtime metadata."""

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class PipelineDefinitionRecord(models.Model):
    """Persistent design-time Pipeline Definition metadata."""

    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=120, db_index=True)
    description = models.TextField(blank=True, default="")
    state = models.CharField(max_length=12, default="DRAFT", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "nexetl_pipeline_definition"
        permissions = (
            ("register_pipeline_definition", "Can register pipeline definition"),
            ("inspect_pipeline_definition", "Can inspect pipeline definition"),
            ("list_pipeline_definition", "Can list pipeline definitions"),
            ("update_pipeline_definition", "Can update pipeline definitions"),
            ("archive_pipeline_definition", "Can archive pipeline definitions"),
            ("design_pipeline_definition", "Can design pipeline definitions"),
            ("publish_pipeline_version", "Can publish pipeline versions"),
            ("run_pipeline_definition", "Can run pipeline definitions"),
            ("inspect_pipeline_run", "Can inspect pipeline runs"),
            ("cancel_pipeline_run", "Can cancel pipeline runs"),
            ("manage_pipeline_schedule", "Can manage pipeline schedules"),
        )


class PipelineDesignRecord(models.Model):
    pipeline = models.OneToOneField(PipelineDefinitionRecord, on_delete=models.CASCADE, related_name="design")
    revision = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "nexetl_pipeline_design"


class PipelineDesignNodeRecord(models.Model):
    design = models.ForeignKey(PipelineDesignRecord, on_delete=models.CASCADE, related_name="nodes")
    id = models.UUIDField(primary_key=True, editable=False)
    type = models.CharField(max_length=12)
    kind = models.CharField(max_length=64, default="legacy")
    label = models.CharField(max_length=120)
    connector_key = models.CharField(max_length=64, null=True, blank=True)
    configuration_version = models.PositiveSmallIntegerField(default=1)
    configuration = models.JSONField(default=dict)
    input_schema = models.JSONField(default=list)
    output_schema = models.JSONField(default=list)
    position_x = models.FloatField()
    position_y = models.FloatField()

    class Meta:
        db_table = "nexetl_pipeline_design_node"


class PipelineDesignEdgeRecord(models.Model):
    design = models.ForeignKey(PipelineDesignRecord, on_delete=models.CASCADE, related_name="edges")
    id = models.UUIDField(primary_key=True, editable=False)
    source_node = models.ForeignKey(PipelineDesignNodeRecord, on_delete=models.CASCADE, related_name="outgoing_edges")
    target_node = models.ForeignKey(PipelineDesignNodeRecord, on_delete=models.CASCADE, related_name="incoming_edges")
    source_port = models.CharField(max_length=64, default="output")
    target_port = models.CharField(max_length=64, default="input")

    class Meta:
        db_table = "nexetl_pipeline_design_edge"
        constraints = [models.UniqueConstraint(fields=["design", "source_node", "source_port", "target_node", "target_port"], name="nexetl_design_unique_edge")]


class ConnectionSecretRecord(models.Model):
    """Opaque secret-provider reference plus encrypted local-provider payload."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_key = models.CharField(max_length=32, default="local_encrypted")
    encrypted_value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "nexetl_connection_secret"


class ConnectionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, db_index=True)
    connector_key = models.CharField(max_length=64, db_index=True)
    description = models.TextField(blank=True, default="")
    configuration = models.JSONField(default=dict)
    secret = models.ForeignKey(ConnectionSecretRecord, null=True, blank=True, on_delete=models.PROTECT, related_name="connections")
    state = models.CharField(max_length=16, default="ENABLED", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "nexetl_connection"
        permissions = (
            ("list_connection", "Can list connections"),
            ("create_connection", "Can create connections"),
            ("inspect_connection", "Can inspect connections"),
            ("update_connection", "Can update connections"),
            ("test_connection", "Can test connections"),
        )


class PipelineVersionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline = models.ForeignKey(PipelineDefinitionRecord, on_delete=models.PROTECT, related_name="versions")
    version = models.PositiveIntegerField()
    design_revision = models.PositiveIntegerField()
    snapshot = models.JSONField()
    snapshot_hash = models.CharField(max_length=64)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="pipeline_versions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "nexetl_pipeline_version"
        constraints = [models.UniqueConstraint(fields=["pipeline", "version"], name="nexetl_pipeline_version_number")]
        ordering = ["-version"]


class PipelineVersionNodeRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.ForeignKey(PipelineVersionRecord, on_delete=models.CASCADE, related_name="nodes")
    design_node_id = models.UUIDField()
    kind = models.CharField(max_length=64)
    category = models.CharField(max_length=16)
    label = models.CharField(max_length=120)
    configuration_version = models.PositiveSmallIntegerField(default=1)
    configuration = models.JSONField(default=dict)
    input_schema = models.JSONField(default=list)
    output_schema = models.JSONField(default=list)
    position_x = models.FloatField()
    position_y = models.FloatField()

    class Meta:
        db_table = "nexetl_pipeline_version_node"
        constraints = [models.UniqueConstraint(fields=["version", "design_node_id"], name="nexetl_version_design_node")]


class PipelineVersionEdgeRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.ForeignKey(PipelineVersionRecord, on_delete=models.CASCADE, related_name="edges")
    design_edge_id = models.UUIDField()
    source_node_id = models.UUIDField()
    source_port = models.CharField(max_length=64, default="output")
    target_node_id = models.UUIDField()
    target_port = models.CharField(max_length=64, default="input")

    class Meta:
        db_table = "nexetl_pipeline_version_edge"


class PipelineScheduleRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline = models.ForeignKey(PipelineDefinitionRecord, on_delete=models.CASCADE, related_name="schedules")
    name = models.CharField(max_length=120)
    enabled = models.BooleanField(default=True, db_index=True)
    expression = models.CharField(max_length=120)
    timezone = models.CharField(max_length=64, default="UTC")
    next_run_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="pipeline_schedules")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "nexetl_pipeline_schedule"
        constraints = [models.UniqueConstraint(fields=["pipeline", "name"], name="nexetl_schedule_name")]


class PipelineRunRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline = models.ForeignKey(PipelineDefinitionRecord, on_delete=models.PROTECT, related_name="runs")
    version = models.ForeignKey(PipelineVersionRecord, on_delete=models.PROTECT, related_name="runs")
    schedule = models.ForeignKey(PipelineScheduleRecord, null=True, blank=True, on_delete=models.SET_NULL, related_name="runs")
    parent_run = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="retry_runs")
    status = models.CharField(max_length=16, default="QUEUED", db_index=True)
    trigger_type = models.CharField(max_length=16, default="MANUAL", db_index=True)
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="pipeline_runs")
    idempotency_key = models.CharField(max_length=128, null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    queued_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    claimed_by = models.CharField(max_length=160, null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    heartbeat_at = models.DateTimeField(null=True, blank=True)
    lease_expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    current_node_id = models.UUIDField(null=True, blank=True)
    cancellation_requested = models.BooleanField(default=False)
    error_code = models.CharField(max_length=80, null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    metrics = models.JSONField(default=dict)
    attempt = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "nexetl_pipeline_run"
        ordering = ["-queued_at"]
        constraints = [
            models.UniqueConstraint(fields=["pipeline", "idempotency_key"], condition=Q(idempotency_key__isnull=False), name="nexetl_run_idempotency"),
            models.UniqueConstraint(fields=["schedule", "scheduled_for"], condition=Q(schedule__isnull=False), name="nexetl_schedule_occurrence"),
        ]
        indexes = [models.Index(fields=["status", "queued_at"], name="nexetl_run_claim_idx")]


class PipelineNodeRunRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(PipelineRunRecord, on_delete=models.CASCADE, related_name="node_runs")
    node_id = models.UUIDField()
    label = models.CharField(max_length=120)
    kind = models.CharField(max_length=64)
    status = models.CharField(max_length=16, default="QUEUED", db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    input_rows = models.BigIntegerField(default=0)
    output_rows = models.BigIntegerField(default=0)
    rejected_rows = models.BigIntegerField(default=0)
    batch_count = models.PositiveIntegerField(default=0)
    error_code = models.CharField(max_length=80, null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    metrics = models.JSONField(default=dict)

    class Meta:
        db_table = "nexetl_pipeline_node_run"
        constraints = [models.UniqueConstraint(fields=["run", "node_id"], name="nexetl_run_node")]


class PipelineRunEventRecord(models.Model):
    run = models.ForeignKey(PipelineRunRecord, on_delete=models.CASCADE, related_name="events")
    node_id = models.UUIDField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(max_length=12, default="INFO")
    event = models.CharField(max_length=80)
    message = models.CharField(max_length=500)
    context = models.JSONField(default=dict)

    class Meta:
        db_table = "nexetl_pipeline_run_event"
        ordering = ["id"]
