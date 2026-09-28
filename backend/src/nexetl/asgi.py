"""ASGI entry point for the NEXETL Django application."""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexetl.settings")

application = get_asgi_application()
