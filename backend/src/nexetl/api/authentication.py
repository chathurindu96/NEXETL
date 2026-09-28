"""DRF authentication adapters for the approved browser session boundary."""

from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import APIException, PermissionDenied


class CsrfRejected(APIException):
    """Represent a session-authentication CSRF rejection without framework detail."""

    status_code = 403
    default_detail = "CSRF validation failed."
    default_code = "csrf_rejected"


class NexetlSessionAuthentication(SessionAuthentication):
    """Translate DRF's CSRF exception into NEXETL's stable external category."""

    def enforce_csrf(self, request) -> None:  # type: ignore[no-untyped-def]
        try:
            super().enforce_csrf(request)
        except PermissionDenied as error:
            raise CsrfRejected() from error
