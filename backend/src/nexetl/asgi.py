"""ASGI entry point for the NEXETL Django application."""

from django.core.asgi import get_asgi_application
from nexetl.configuration import configure_django_settings_module


configure_django_settings_module()

application = get_asgi_application()
