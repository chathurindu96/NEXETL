"""Framework-independent use cases for Increment 1 Pipeline Definitions."""

from .ports import PipelineDefinitionStore
from pipelines.domain import PipelineDefinition, PipelineDefinitionId


class RegisterPipelineDefinition:
    """Create and persist a server-generated Pipeline Definition identity."""

    def __init__(self, store: PipelineDefinitionStore) -> None:
        self._store = store

    def execute(self) -> PipelineDefinition:
        pipeline_definition = PipelineDefinition(PipelineDefinitionId.generate())
        self._store.create(pipeline_definition)
        return pipeline_definition


class InspectPipelineDefinition:
    """Retrieve a Pipeline Definition identity by its governed identifier."""

    def __init__(self, store: PipelineDefinitionStore) -> None:
        self._store = store

    def execute(self, pipeline_definition_id: PipelineDefinitionId) -> PipelineDefinition | None:
        return self._store.get(pipeline_definition_id)
