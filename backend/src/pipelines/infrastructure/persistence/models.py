"""Physical PostgreSQL representation of the identity-only Pipeline Definition."""

from django.db import models


class PipelineDefinitionRecord(models.Model):
    """The governed `nexetl_pipeline_definition` table: UUID primary key only."""

    id = models.UUIDField(primary_key=True, editable=False)

    class Meta:
        db_table = "nexetl_pipeline_definition"
