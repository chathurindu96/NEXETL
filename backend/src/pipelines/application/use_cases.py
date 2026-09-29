"""Framework-independent use cases for Increment 1 Pipeline Definitions."""

from .ports import PipelineDefinitionStore
from pipelines.domain import PipelineDefinition, PipelineDefinitionId


class RegisterPipelineDefinition:
    """Create and persist a server-generated Pipeline Definition identity."""

    def __init__(self, store: PipelineDefinitionStore) -> None:
        self._store = store

    def execute(self, name: str, description: str = "") -> PipelineDefinition:
        pipeline_definition = PipelineDefinition.create(name, description)
        self._store.create(pipeline_definition)
        return pipeline_definition


class InspectPipelineDefinition:
    """Retrieve a Pipeline Definition identity by its governed identifier."""

    def __init__(self, store: PipelineDefinitionStore) -> None:
        self._store = store

    def execute(self, pipeline_definition_id: PipelineDefinitionId) -> PipelineDefinition | None:
        return self._store.get(pipeline_definition_id)


class ListPipelineDefinitions:
    def __init__(self, store: PipelineDefinitionStore) -> None:
        self._store = store

    def execute(
        self,
        *,
        page: int,
        page_size: int,
        search: str = "",
        state: str | None = None,
        sort: str = "-updatedAt",
    ) -> tuple[list[PipelineDefinition], int]:
        return self._store.list(
            page=page, page_size=page_size, search=search, state=state, sort=sort
        )


class UpdatePipelineDefinition:
    def __init__(self, store: PipelineDefinitionStore) -> None:
        self._store = store

    def execute(
        self, pipeline_definition_id: PipelineDefinitionId, name: str, description: str
    ) -> PipelineDefinition | None:
        current = self._store.get(pipeline_definition_id)
        if current is None:
            return None
        return self._store.update(current.update_metadata(name, description))


class ArchivePipelineDefinition:
    def __init__(self, store: PipelineDefinitionStore) -> None:
        self._store = store

    def execute(self, pipeline_definition_id: PipelineDefinitionId) -> PipelineDefinition | None:
        current = self._store.get(pipeline_definition_id)
        if current is None:
            return None
        return self._store.update(current.archive())
