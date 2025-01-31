import json
import pytest
from cryptography import fernet
from moto import mock_aws
from unittest.mock import patch, Mock
from testapp.configs import models
from mixer.backend.django import mixer
from django.test import override_settings

pytestmark = pytest.mark.django_db


def test_model_text_field() -> None:
    instance = models.ModelTextStatic()
    instance.secret = "supersecret"
    instance.save()

    instance = models.ModelTextStatic.objects.first()
    assert instance.secret.get() == "supersecret"
    instance.save()
    assert instance.secret.get() == "supersecret"
    instance = models.ModelTextStatic.objects.first()
    assert instance.secret.get() == "supersecret"

    crypter = fernet.Fernet(b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=")
    ciphertext = instance.secret.ciphertext
    decrypted = crypter.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    assert decrypted == "supersecret"

    assert instance.secret.plaintext == "supersecret"
    assert instance.secret.get() == "supersecret"
    assert str(instance.secret) == "supersecret"
    assert repr(instance.secret) == "supersecret"


def test_model_json_field_dict() -> None:
    instance = models.ModelJSONStatic()
    instance.secret = {"test": "supersecret"}
    assert instance.secret == {"test": "supersecret"}
    instance.save()
    assert instance.secret == {"test": "supersecret"}

    instance = models.ModelJSONStatic.objects.first()
    assert instance.secret == {"test": "supersecret"}


def test_model_json_field_list() -> None:
    instance = models.ModelJSONStatic()
    instance.secret = [1, 2, 3]
    assert instance.secret == [1, 2, 3]
    instance.save()
    assert instance.secret == [1, 2, 3]

    instance = models.ModelJSONStatic.objects.first()
    assert instance.secret == [1, 2, 3]


def test_model_json_field_mixed() -> None:
    model = mixer.blend(
        models.ModelJSONStatic,
        config={"test": "supersecret"},
        secret=None,
    )
    assert model.config == {"test": "supersecret"}


@patch("secrets_fields.fields.SecretField.get_prep_value")
def test_json_field_encrypted_convert(mock_get_prep_value: Mock) -> None:
    mock_get_prep_value.return_value = json.dumps({"test": "123"})
    instance = models.ModelJSONStatic()
    instance.secret = {"test": "123"}
    instance.save()

    models.ModelJSONStatic.objects.first()


@mock_aws
@pytest.mark.django_db
def test_model_text_field_secrets_manager() -> None:
    instance = models.ModelTextAWS()
    instance.secret = "supersecret"
    instance.save()

    instance = models.ModelTextAWS.objects.first()
    assert instance.secret.get() == "supersecret"
    instance.save()
    assert instance.secret.get() == "supersecret"
    instance = models.ModelTextAWS.objects.first()
    assert instance.secret.get() == "supersecret"
    assert instance.secret.ciphertext == "/path/9a618248b64db62d15b300a07b00580b"

    assert instance.secret.plaintext == "supersecret"
    assert instance.secret.get() == "supersecret"
    assert str(instance.secret) == "supersecret"
    assert repr(instance.secret) == "supersecret"


@mock_aws
@pytest.mark.django_db
def test_model_json_field_dict_secrets_manager() -> None:
    instance = models.ModelJSONAWS()
    instance.secret = {"test": "supersecret"}
    instance.save()

    assert instance.secret == {"test": "supersecret"}

    instance = models.ModelJSONAWS.objects.first()
    assert instance.secret == {"test": "supersecret"}


@mock_aws
@pytest.mark.django_db
def test_model_json_field_list_secrets_manager() -> None:
    instance = models.ModelJSONAWS()
    instance.secret = [1, 2, 3]
    instance.save()

    assert instance.secret == [1, 2, 3]

    instance = models.ModelJSONAWS.objects.first()
    assert instance.secret == [1, 2, 3]


@mock_aws
@pytest.mark.django_db
def test_model_json_field_mixed_secrets_manager() -> None:
    model = mixer.blend(
        models.ModelJSONAWS,
        secret={"test": "supersecret"},
    )
    assert model.secret == {"test": "supersecret"}


@mock_aws
@pytest.mark.django_db
@override_settings(
    DJANGO_SECRETS_FIELDS={
        "aws": {
            "backend": "secrets_fields.backends.secretsmanager.SecretsManagerBackend",
            "prefix": "/path/",
            "role_arn_rw": "arn:aws:iam::123456789012:role/role_name_rw",
        },
        "static": {
            "backend": "secrets_fields.backends.encrypted.EncryptedBackend",
            "encryption_key": b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=",
        },
    }
)
def test_model_json_field_list_secrets_manager_role() -> None:
    instance = models.ModelJSONAWS()
    instance.secret = [1, 2, 3]
    instance.save()

    assert instance.secret == [1, 2, 3]

    instance = models.ModelJSONAWS.objects.first()
    assert instance.secret == [1, 2, 3]
