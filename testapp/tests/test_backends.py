import pytest
from secrets_fields.backends.backends import BaseSecretsBackend
from secrets_fields.backends.encrypted import EncryptedBackend
from django.core.exceptions import ImproperlyConfigured


def test_encrypt_raises_not_implemented_error():
    backend = BaseSecretsBackend({})
    with pytest.raises(NotImplementedError):
        backend.encrypt("plaintext")


def test_decrypt_raises_not_implemented_error():
    backend = BaseSecretsBackend({})
    with pytest.raises(NotImplementedError):
        backend.decrypt("ciphertext")


def test_encrypted_no_key():
    backend = EncryptedBackend({})
    with pytest.raises(ImproperlyConfigured):
        backend.encrypt("plaintext")
