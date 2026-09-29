"""Physical PostgreSQL representation of the identity-only Pipeline Definition."""

from django.db import models


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
    label = models.CharField(max_length=120)
    connector_key = models.CharField(max_length=64, null=True, blank=True)
    position_x = models.FloatField()
    position_y = models.FloatField()

    class Meta:
        db_table = "nexetl_pipeline_design_node"


class PipelineDesignEdgeRecord(models.Model):
    design = models.ForeignKey(PipelineDesignRecord, on_delete=models.CASCADE, related_name="edges")
    id = models.UUIDField(primary_key=True, editable=False)
    source_node = models.ForeignKey(PipelineDesignNodeRecord, on_delete=models.CASCADE, related_name="outgoing_edges")
    target_node = models.ForeignKey(PipelineDesignNodeRecord, on_delete=models.CASCADE, related_name="incoming_edges")

    class Meta:
        db_table = "nexetl_pipeline_design_edge"
        constraints = [models.UniqueConstraint(fields=["design", "source_node", "target_node"], name="nexetl_design_unique_edge")]
