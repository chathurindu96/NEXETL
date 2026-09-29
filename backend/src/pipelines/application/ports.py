"""Application-owned ports for the Pipeline Definition capability."""

from typing import Protocol

from pipelines.domain import PipelineDefinition, PipelineDefinitionId


class PipelineDefinitionStore(Protocol):
    """Persist and retrieve the narrowly governed Pipeline Definition entity."""

    def create(self, pipeline_definition: PipelineDefinition) -> None: ...

    def get(self, pipeline_definition_id: PipelineDefinitionId) -> PipelineDefinition | None: ...

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str,
        state: str | None,
        sort: str,
    ) -> tuple[list[PipelineDefinition], int]: ...

    def update(self, pipeline_definition: PipelineDefinition) -> PipelineDefinition: ...
