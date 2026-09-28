"""Framework-independent identifiers for the Pipeline Definition domain."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class PipelineDefinitionId:
    """The immutable, canonical public identifier of a Pipeline Definition."""

    value: UUID

    @classmethod
    def generate(cls) -> "PipelineDefinitionId":
        """Generate a server-owned UUID v4 identity."""
        return cls(uuid4())

    @classmethod
    def parse(cls, value: str) -> "PipelineDefinitionId":
        """Parse a canonical UUID string supplied at an adapter boundary."""
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)
