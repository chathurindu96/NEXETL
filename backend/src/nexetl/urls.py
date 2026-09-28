"""Root URL composition for the NEXETL backend."""

from django.urls import URLPattern, URLResolver, include, path

from nexetl.operational import service_index


# The API prefix is a composition seam; feature routes arrive only in authorized slices.
urlpatterns: list[URLPattern | URLResolver] = [
    path("", service_index, name="service-index"),
    path("api/", include("pipelines.api.urls")),
]
