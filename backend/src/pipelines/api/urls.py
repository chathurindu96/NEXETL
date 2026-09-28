"""Pipeline API URL composition point; feature routes are added by later tickets."""

from django.urls import URLPattern, URLResolver


urlpatterns: list[URLPattern | URLResolver] = []
