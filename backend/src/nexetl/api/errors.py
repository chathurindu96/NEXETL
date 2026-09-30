"""Centralized safe translation of DRF failures into the Increment 1 contract."""

import logging

from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response

from nexetl.api.authentication import CsrfRejected


logger = logging.getLogger("nexetl.api")


class NexetlAPIError(APIException):
    """Safe application error whose symbolic code is part of the REST contract."""

    def __init__(self, code: str, message: str, *, http_status: int = 400, category: str = "request", details: object | None = None) -> None:
        super().__init__(message, code=code)
        self.nexetl_code = code
        self.public_message = message
        self.status_code = http_status
        self.category = category
        self.public_details = details


def exception_handler(exc: Exception, context: dict[str, object]) -> Response:
    """Return safe, stable NEXETL errors without framework exception details."""
    code, category, message, http_status, details = _translate(exc)
    payload: dict[str, object] = {
        "code": code,
        "category": category,
        "message": message,
    }
    if details is not None:
        payload["details"] = details
    return Response(payload, status=http_status)


def _translate(exc: Exception) -> tuple[str, str, str, int, object | None]:
    if isinstance(exc, NexetlAPIError):
        return exc.nexetl_code, exc.category, exc.public_message, exc.status_code, exc.public_details
    if isinstance(exc, CsrfRejected):
        return (
            "NEXETL_CSRF_REJECTED",
            "security",
            "CSRF validation failed.",
            status.HTTP_403_FORBIDDEN,
            None,
        )
    if isinstance(exc, ValidationError):
        return (
            "NEXETL_VALIDATION_FAILED",
            "validation",
            "The request contains invalid input.",
            status.HTTP_400_BAD_REQUEST,
            exc.detail,
        )
    if isinstance(exc, NotAuthenticated):
        return (
            "NEXETL_AUTHENTICATION_REQUIRED",
            "authentication",
            "Authentication is required.",
            status.HTTP_401_UNAUTHORIZED,
            None,
        )
    if isinstance(exc, PermissionDenied):
        return (
            "NEXETL_AUTHORIZATION_DENIED",
            "authorization",
            "You are not authorized for this operation.",
            status.HTTP_403_FORBIDDEN,
            None,
        )
    if isinstance(exc, NotFound):
        return (
            "NEXETL_PIPELINE_DEFINITION_NOT_FOUND",
            "not_found",
            "The Pipeline Definition was not found.",
            status.HTTP_404_NOT_FOUND,
            None,
        )
    if isinstance(exc, MethodNotAllowed):
        return (
            "NEXETL_METHOD_NOT_ALLOWED",
            "request",
            "The request method is not allowed.",
            status.HTTP_405_METHOD_NOT_ALLOWED,
            None,
        )
    logger.exception("Unhandled API exception translated to a safe response")
    return (
        "NEXETL_INTERNAL_ERROR",
        "internal",
        "An unexpected service error occurred.",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        None,
    )
