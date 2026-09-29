"""Structural verification of the governed Pipeline Definition persistence shape."""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexetl.settings")
django.setup()

from pipelines.infrastructure.persistence.models import PipelineDefinitionRecord


def test_pipeline_definition_record_has_the_increment_two_registry_shape() -> None:
    fields = PipelineDefinitionRecord._meta.local_fields

    assert PipelineDefinitionRecord._meta.db_table == "nexetl_pipeline_definition"
    assert [field.name for field in fields] == [
        "id", "name", "description", "state", "created_at", "updated_at"
    ]
    assert fields[0].primary_key is True
