"""Backend-authoritative capability checks shared by REST adapters."""

from django.http import HttpRequest
from rest_framework.exceptions import NotAuthenticated, PermissionDenied


def require_capability(request: HttpRequest, permission: str) -> None:
    if not request.user or not request.user.is_authenticated:
        raise NotAuthenticated()
    if not request.user.has_perm(permission):
        raise PermissionDenied()
