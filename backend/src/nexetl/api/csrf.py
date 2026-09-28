"""Safe CSRF failure translation for the direct browser-to-API profile."""

from django.http import HttpRequest, JsonResponse


def csrf_failure(_: HttpRequest, reason: str = "") -> JsonResponse:
    """Return the governed safe contract without leaking CSRF failure internals."""
    return JsonResponse(
        {
            "code": "NEXETL_CSRF_REJECTED",
            "category": "security",
            "message": "CSRF validation failed.",
        },
        status=403,
    )
