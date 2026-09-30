"""Django model discovery bridge for the pipelines application."""

from pipelines.infrastructure.persistence.models import (
    ConnectionRecord,
    ConnectionSecretRecord,
    PipelineDefinitionRecord,
    PipelineDesignEdgeRecord,
    PipelineDesignNodeRecord,
    PipelineDesignRecord,
    PipelineNodeRunRecord,
    PipelineRunEventRecord,
    PipelineRunRecord,
    PipelineScheduleRecord,
    PipelineVersionEdgeRecord,
    PipelineVersionNodeRecord,
    PipelineVersionRecord,
)

__all__ = [name for name in globals() if name.endswith("Record")]
