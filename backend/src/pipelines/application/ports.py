"""Application-owned ports for the Pipeline Definition capability."""

from typing import Protocol

from pipelines.domain import PipelineDefinition, PipelineDefinitionId


class PipelineDefinitionStore(Protocol):
    """Persist and retrieve the narrowly governed Pipeline Definition entity."""

    def create(self, pipeline_definition: PipelineDefinition) -> None: ...

    def get(self, pipeline_definition_id: PipelineDefinitionId) -> PipelineDefinition | None: ...
