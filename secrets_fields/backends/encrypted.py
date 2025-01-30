from cryptography import fernet
from .backends import BaseSecretsBackend
from django.core.exceptions import ImproperlyConfigured
from ..util import get_config


class EncryptedBackend(BaseSecretsBackend):
    """Encrypted field backend

    Uses an encryption key to encrypt and decrypt values
    """

    @property
    def _crypter(self) -> fernet.Fernet:
        key = self.config.get("encryption_key", None)
        if not key:
            raise ImproperlyConfigured(
                "DJANGO_SECRETS_FIELDS['encryption_key'] must be set"
            )

        return fernet.Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Create secret using the backend"""
        encrypted: bytes = self._crypter.encrypt(plaintext.encode("utf-8"))
        return encrypted.decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Get secret from backend

        Args:
            ciphertext (str): ciphertext

        Returns:
            str: plaintext secret
        """
        decrypted: bytes = self._crypter.decrypt(ciphertext.encode("utf-8"))
        return decrypted.decode("utf-8")
