"""Django settings composed from validated NEXETL bootstrap configuration."""

from pathlib import Path

from nexetl.configuration import load_backend_configuration


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIGURATION = load_backend_configuration()

SECRET_KEY = CONFIGURATION.secret_key
DEBUG = CONFIGURATION.debug
ALLOWED_HOSTS = list(CONFIGURATION.allowed_hosts)

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "nexetl.urls"
TEMPLATES: list[dict[str, object]] = []
WSGI_APPLICATION = "nexetl.wsgi.application"
ASGI_APPLICATION = "nexetl.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": CONFIGURATION.database.name,
        "USER": CONFIGURATION.database.user,
        "PASSWORD": CONFIGURATION.database.password,
        "HOST": CONFIGURATION.database.host,
        "PORT": CONFIGURATION.database.port,
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = CONFIGURATION.session_cookie_secure
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = CONFIGURATION.csrf_cookie_secure
