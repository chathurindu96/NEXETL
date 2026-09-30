"""Replaceable secret-provider boundary with encrypted local persistence."""

import base64
import hashlib
from typing import Protocol
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from pipelines.infrastructure.persistence.models import ConnectionSecretRecord


class SecretUnavailable(RuntimeError):
    pass


class SecretProvider(Protocol):
    def store(self, value: str) -> UUID: ...
    def replace(self, reference: UUID, value: str) -> None: ...
    def resolve(self, reference: UUID) -> str: ...


class LocalEncryptedSecretProvider:
    provider_key = "local_encrypted"

    def __init__(self) -> None:
        configured = settings.CONFIGURATION.connection_secret_key
        if not configured and not settings.DEBUG:
            raise SecretUnavailable("The Connection secret provider is not configured.")
        material = configured or settings.SECRET_KEY
        key = base64.urlsafe_b64encode(hashlib.sha256(material.encode("utf-8")).digest())
        self._cipher = Fernet(key)

    def store(self, value: str) -> UUID:
        if not value:
            raise ValueError("A non-empty secret is required.")
        record = ConnectionSecretRecord.objects.create(
            provider_key=self.provider_key,
            encrypted_value=self._cipher.encrypt(value.encode("utf-8")).decode("ascii"),
        )
        return record.id

    def replace(self, reference: UUID, value: str) -> None:
        if not value:
            raise ValueError("A non-empty secret is required.")
        record = ConnectionSecretRecord.objects.get(id=reference, provider_key=self.provider_key)
        record.encrypted_value = self._cipher.encrypt(value.encode("utf-8")).decode("ascii")
        record.save(update_fields=["encrypted_value", "updated_at"])

    def resolve(self, reference: UUID) -> str:
        try:
            record = ConnectionSecretRecord.objects.get(id=reference, provider_key=self.provider_key)
            return self._cipher.decrypt(record.encrypted_value.encode("ascii")).decode("utf-8")
        except (ConnectionSecretRecord.DoesNotExist, InvalidToken) as error:
            raise SecretUnavailable("The Connection secret is unavailable.") from error
