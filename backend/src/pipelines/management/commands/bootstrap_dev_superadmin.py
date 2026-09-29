"""Explicitly guarded local-development superadmin bootstrap command."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or repair the explicitly enabled local development superadmin."

    def handle(self, *args, **options) -> None:  # type: ignore[no-untyped-def]
        config = settings.CONFIGURATION.development_superadmin
        if not settings.DEBUG:
            raise CommandError("Development superadmin bootstrap requires DEBUG=true.")
        if not config.enabled:
            raise CommandError("Development superadmin bootstrap requires NEXETL_DEV_SUPERADMIN_ENABLED=true.")
        user, _ = get_user_model().objects.get_or_create(username=config.username)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(config.password)
        user.save()
        self.stdout.write(self.style.SUCCESS("Development superadmin is ready."))
