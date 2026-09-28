"""Framework-independent Pipeline Definition domain entity."""

from dataclasses import dataclass

from .identifiers import PipelineDefinitionId


@dataclass(frozen=True)
class PipelineDefinition:
    """The governed Increment 1 Pipeline Definition: immutable identity only."""

    id: PipelineDefinitionId
