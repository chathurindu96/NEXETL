"""Django ORM implementation of the application-owned persistence port."""

from pipelines.domain import PipelineDefinition, PipelineDefinitionId, PipelineState
from .models import PipelineDefinitionRecord


class DjangoPipelineDefinitionStore:
    """Persist only the governed Pipeline Definition UUID identity."""

    def create(self, pipeline_definition: PipelineDefinition) -> None:
        PipelineDefinitionRecord.objects.create(
            id=pipeline_definition.id.value,
            name=pipeline_definition.name,
            description=pipeline_definition.description,
            state=pipeline_definition.state,
        )

    def get(self, pipeline_definition_id: PipelineDefinitionId) -> PipelineDefinition | None:
        record = PipelineDefinitionRecord.objects.filter(id=pipeline_definition_id.value).first()
        if record is None:
            return None
        return self._entity(record)

    def list(
        self, *, page: int, page_size: int, search: str, state: str | None, sort: str
    ) -> tuple[list[PipelineDefinition], int]:
        ordering = {
            "updatedAt": "updated_at",
            "-updatedAt": "-updated_at",
            "createdAt": "created_at",
            "-createdAt": "-created_at",
            "name": "name",
            "-name": "-name",
        }[sort]
        records = PipelineDefinitionRecord.objects.all()
        if search:
            records = records.filter(name__icontains=search)
        if state:
            records = records.filter(state=state)
        total = records.count()
        start = (page - 1) * page_size
        return (
            [self._entity(record) for record in records.order_by(ordering)[start : start + page_size]],
            total,
        )

    def update(self, pipeline_definition: PipelineDefinition) -> PipelineDefinition:
        record = PipelineDefinitionRecord.objects.get(id=pipeline_definition.id.value)
        record.name = pipeline_definition.name
        record.description = pipeline_definition.description
        record.state = pipeline_definition.state
        record.save(update_fields=["name", "description", "state", "updated_at"])
        return self._entity(record)

    @staticmethod
    def _entity(record: PipelineDefinitionRecord) -> PipelineDefinition:
        return PipelineDefinition(
            PipelineDefinitionId(record.id),
            record.name,
            record.description,
            PipelineState(record.state),
            record.created_at,
            record.updated_at,
        )
