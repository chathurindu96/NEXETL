"""Django ORM implementation of the application-owned persistence port."""

from pipelines.domain import PipelineDefinition, PipelineDefinitionId
from .models import PipelineDefinitionRecord


class DjangoPipelineDefinitionStore:
    """Persist only the governed Pipeline Definition UUID identity."""

    def create(self, pipeline_definition: PipelineDefinition) -> None:
        PipelineDefinitionRecord.objects.create(id=pipeline_definition.id.value)

    def get(self, pipeline_definition_id: PipelineDefinitionId) -> PipelineDefinition | None:
        record = PipelineDefinitionRecord.objects.filter(id=pipeline_definition_id.value).first()
        if record is None:
            return None
        return PipelineDefinition(PipelineDefinitionId(record.id))
