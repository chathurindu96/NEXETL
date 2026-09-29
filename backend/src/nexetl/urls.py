"""Root URL composition for the NEXETL backend."""

from django.urls import URLPattern, URLResolver, include, path

from nexetl.operational import service_index
from nexetl.api.auth import session_login, session_logout, session_state


# The API prefix is a composition seam; feature routes arrive only in authorized slices.
urlpatterns: list[URLPattern | URLResolver] = [
    path("", service_index, name="service-index"),
    path("api/auth/session/", session_state, name="auth-session"),
    path("api/auth/login/", session_login, name="auth-login"),
    path("api/auth/logout/", session_logout, name="auth-logout"),
    path("api/", include("pipelines.api.urls")),
]
