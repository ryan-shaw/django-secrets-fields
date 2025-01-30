import pytest
from cryptography import fernet
from moto import mock_aws
from testapp.configs.models import TestModel
from mixer.backend.django import mixer
from django.test import override_settings

pytestmark = pytest.mark.django_db


def test_model_text_field():
    instance = TestModel()
    instance.secret = "supersecret"
    instance.save()

    instance = TestModel.objects.first()
    assert instance.secret.get() == "supersecret"
    instance.save()
    assert instance.secret.get() == "supersecret"
    instance = TestModel.objects.first()
    assert instance.secret.get() == "supersecret"

    crypter = fernet.Fernet(b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=")
    ciphertext = instance.secret.ciphertext
    decrypted = crypter.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    assert decrypted == "supersecret"

    assert instance.secret.plaintext == "supersecret"
    assert instance.secret.get() == "supersecret"
    assert str(instance.secret) == "supersecret"
    assert repr(instance.secret) == "supersecret"


def test_model_json_field_dict():
    instance = TestModel()
    instance.config = {"test": "supersecret"}
    assert instance.config == {"test": "supersecret"}
    instance.save()
    assert instance.config == {"test": "supersecret"}

    instance = TestModel.objects.first()
    assert instance.config == {"test": "supersecret"}


def test_model_json_field_list():
    instance = TestModel()
    instance.config = [1, 2, 3]
    assert instance.config == [1, 2, 3]
    instance.save()
    assert instance.config == [1, 2, 3]

    instance = TestModel.objects.first()
    assert instance.config == [1, 2, 3]


def test_model_json_field_mixed():
    model = mixer.blend(
        TestModel,
        config={"test": "supersecret"},
        config_aws=None,
        secret_aws=None,
        secret=None,
    )
    assert model.config == {"test": "supersecret"}


@mock_aws
@pytest.mark.django_db
def test_model_text_field_secrets_manager():
    instance = TestModel()
    instance.secret_aws = "supersecret"
    instance.save()

    instance = TestModel.objects.first()
    assert instance.secret_aws.get() == "supersecret"
    instance.save()
    assert instance.secret_aws.get() == "supersecret"
    instance = TestModel.objects.first()
    assert instance.secret_aws.get() == "supersecret"
    assert instance.secret_aws.ciphertext == "/path/9a618248b64db62d15b300a07b00580b"

    assert instance.secret_aws.plaintext == "supersecret"
    assert instance.secret_aws.get() == "supersecret"
    assert str(instance.secret_aws) == "supersecret"
    assert repr(instance.secret_aws) == "supersecret"


@mock_aws
@pytest.mark.django_db
def test_model_json_field_dict_secrets_manager():
    instance = TestModel()
    instance.config_aws = {"test": "supersecret"}
    instance.save()

    assert instance.config_aws == {"test": "supersecret"}

    instance = TestModel.objects.first()
    assert instance.config_aws == {"test": "supersecret"}


@mock_aws
@pytest.mark.django_db
def test_model_json_field_list_secrets_manager():
    instance = TestModel()
    instance.config_aws = [1, 2, 3]
    instance.save()

    assert instance.config_aws == [1, 2, 3]

    instance = TestModel.objects.first()
    assert instance.config_aws == [1, 2, 3]


@mock_aws
@pytest.mark.django_db
def test_model_json_field_mixed_secrets_manager():
    model = mixer.blend(
        TestModel,
        config_aws={"test": "supersecret"},
        config=None,
        secret_aws=None,
        secret=None,
    )
    assert model.config_aws == {"test": "supersecret"}


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
def test_model_json_field_list_secrets_manager_role():
    instance = TestModel()
    instance.config_aws = [1, 2, 3]
    instance.save()

    assert instance.config_aws == [1, 2, 3]

    instance = TestModel.objects.first()
    assert instance.config_aws == [1, 2, 3]
