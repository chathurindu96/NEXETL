"""WSGI entry point for the NEXETL Django application."""

from django.core.wsgi import get_wsgi_application
from nexetl.configuration import configure_django_settings_module


configure_django_settings_module()

application = get_wsgi_application()
