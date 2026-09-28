"""Narrow non-business operational responses owned by backend composition."""

from django.http import JsonResponse


def service_index(_request) -> JsonResponse:  # type: ignore[no-untyped-def]
    """Confirm that the backend process is reachable without exposing internals."""
    return JsonResponse(
        {
            "service": "NEXETL Backend",
            "message": "NEXETL backend is running.",
            "apiBase": "/api/",
        }
    )
