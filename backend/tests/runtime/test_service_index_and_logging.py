"""Runtime-operational contract checks without business data disclosure."""

import logging

from django.test import Client


def test_service_index_returns_safe_metadata_and_request_log(caplog) -> None:  # type: ignore[no-untyped-def]
    caplog.set_level(logging.INFO, logger="nexetl.request")

    response = Client().get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "NEXETL Backend",
        "message": "NEXETL backend is running.",
        "apiBase": "/api/",
    }
    assert "PipelineDefinition" not in response.content.decode()
    assert any(record.getMessage().startswith("GET / 200 ") for record in caplog.records)
