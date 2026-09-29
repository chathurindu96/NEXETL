"""Minimal local session-authentication endpoints using Django's auth system."""

import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST


@require_GET
def session_state(request: HttpRequest) -> JsonResponse:
    if request.user.is_authenticated:
        return JsonResponse({"authenticated": True, "username": request.user.get_username()})
    return JsonResponse({"authenticated": False})


@require_POST
def session_login(request: HttpRequest) -> HttpResponse:
    try:
        payload = json.loads(request.body)
        username = payload.get("username", "")
        password = payload.get("password", "")
    except (json.JSONDecodeError, AttributeError):
        username = password = ""
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse(
            {"code": "NEXETL_AUTHENTICATION_FAILED", "category": "authentication", "message": "Invalid username or password."},
            status=401,
        )
    login(request, user)
    return HttpResponse(status=204)


@require_POST
def session_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return HttpResponse(status=204)
