"""Unit tests for the governed identity-only Pipeline Definition domain."""

from pipelines.application import InspectPipelineDefinition, RegisterPipelineDefinition
from pipelines.domain import PipelineDefinition, PipelineDefinitionId


class InMemoryPipelineDefinitionStore:
    def __init__(self) -> None:
        self.values: dict[PipelineDefinitionId, PipelineDefinition] = {}

    def create(self, pipeline_definition: PipelineDefinition) -> None:
        self.values[pipeline_definition.id] = pipeline_definition

    def get(self, pipeline_definition_id: PipelineDefinitionId) -> PipelineDefinition | None:
        return self.values.get(pipeline_definition_id)


def test_register_creates_a_canonical_uuid_identity_only() -> None:
    result = RegisterPipelineDefinition(InMemoryPipelineDefinitionStore()).execute()

    assert isinstance(result.id, PipelineDefinitionId)
    assert str(result.id) == str(result.id.value)


def test_inspect_returns_the_persisted_identity_or_none() -> None:
    store = InMemoryPipelineDefinitionStore()
    created = RegisterPipelineDefinition(store).execute()

    assert InspectPipelineDefinition(store).execute(created.id) == created
    assert InspectPipelineDefinition(store).execute(PipelineDefinitionId.generate()) is None
