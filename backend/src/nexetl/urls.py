"""Root URL composition for the NEXETL backend."""

from django.urls import URLPattern, URLResolver


# Feature routes are added only by their authorized implementation slices.
urlpatterns: list[URLPattern | URLResolver] = []
