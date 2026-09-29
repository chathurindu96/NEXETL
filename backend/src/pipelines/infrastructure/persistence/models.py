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
