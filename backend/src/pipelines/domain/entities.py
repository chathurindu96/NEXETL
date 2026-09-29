"""Framework-independent Pipeline Definition domain entity."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .identifiers import PipelineDefinitionId


class PipelineState(StrEnum):
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class PipelineDefinition:
    id: PipelineDefinitionId
    name: str
    description: str = ""
    state: PipelineState = PipelineState.DRAFT
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(cls, name: str, description: str = "") -> "PipelineDefinition":
        name = name.strip()
        description = description.strip()
        if not 1 <= len(name) <= 120 or len(description) > 1000:
            raise ValueError("Invalid Pipeline Definition metadata")
        return cls(PipelineDefinitionId.generate(), name, description)

    def update_metadata(self, name: str, description: str) -> "PipelineDefinition":
        if self.state is PipelineState.ARCHIVED:
            raise ValueError("NEXETL_PIPELINE_ARCHIVED")
        name = name.strip()
        description = description.strip()
        if not 1 <= len(name) <= 120 or len(description) > 1000:
            raise ValueError("Invalid Pipeline Definition metadata")
        return PipelineDefinition(
            self.id, name, description, self.state, self.created_at, self.updated_at
        )

    def archive(self) -> "PipelineDefinition":
        return PipelineDefinition(
            self.id,
            self.name,
            self.description,
            PipelineState.ARCHIVED,
            self.created_at,
            self.updated_at,
        )
