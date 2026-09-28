"""Root URL composition for the NEXETL backend."""

from django.urls import URLPattern, URLResolver, include, path


# The API prefix is a composition seam; feature routes arrive only in authorized slices.
urlpatterns: list[URLPattern | URLResolver] = [
    path("api/", include("pipelines.api.urls")),
]
