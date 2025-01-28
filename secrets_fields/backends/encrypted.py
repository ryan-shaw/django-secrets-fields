from cryptography import fernet
from .backends import BaseSecretsBackend
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class EncryptedBackend(BaseSecretsBackend):
    """Encrypted field backend

    Uses an encryption key to encrypt and decrypt values
    """

    @property
    def crypter(self) -> fernet.Fernet:
        key = getattr(settings, "DJANGO_SECRET_FIELDS_ENCRYPTION_KEY", None)
        if not key:
            raise ImproperlyConfigured(
                "DJANGO_SECRET_FIELDS_ENCRYPTION_KEY must be set"
            )

        return fernet.Fernet(key)

    def get_ciphertext(self, secret_value: str) -> str:
        encrypted : bytes = self.crypter.encrypt(secret_value.encode("utf-8"))
        return encrypted.decode('utf-8')

    def create_secret(self, *args : str) -> str:
        """Create secret using the backend"""
        return self.get_ciphertext(args[0])

    def get_secret(self, secret_name: str) -> str:
        """Get secret from backend

        Args:
            secret_name (str): name of the secret

        Returns:
            str: plaintext secret
        """
        decrypted : bytes = self.crypter.decrypt(secret_name.encode("utf-8"))
        return decrypted.decode("utf-8")
