import json
import pytest
from cryptography import fernet
from moto import mock_aws
from unittest.mock import patch
from testapp.configs import models
from mixer.backend.django import mixer
from django.test import override_settings
from django.db import connection
from secrets_fields.exceptions import DecryptionException

from secrets_fields.management.commands.migrate_encrypted import (
    Command as MigrateEncryptedCommand,
)

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
    ciphertext = instance.secret.ciphertext.split("|")[-1]
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


@override_settings(
    DJANGO_SECRETS_FIELDS_MIGRATE=True,
)
def test_json_field_encrypted_convert_plaintext() -> None:
    with patch(
        "secrets_fields.fields.SecretField.get_prep_value"
    ) as mock_get_prep_value:
        mock_get_prep_value.return_value = json.dumps({"test": "123"})
        instance = models.ModelJSONStatic()
        instance.secret = {"test": "123"}
        instance.save()

    instance = models.ModelJSONStatic.objects.first()
    assert instance.secret == {"test": "123"}

    # Raw SQL to check the value is not encrypted
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {models.ModelJSONStatic._meta.db_table}")
        row = cursor.fetchone()
        assert row[1] == '{"test": "123"}'

        MigrateEncryptedCommand().handle()

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {models.ModelJSONStatic._meta.db_table}")
        row = cursor.fetchone()
        assert row[1] != '{"test": "123"}'
        # Decrypt the value to make sure it's valid
        crypter = fernet.Fernet(b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=")
        decrypted = crypter.decrypt(row[1].replace("v1|", "").encode("utf-8")).decode(
            "utf-8"
        )
        assert json.loads(decrypted) == {"test": "123"}


def test_json_field_encrypted_convert_non_versioned() -> None:
    with patch(
        "secrets_fields.fields.SecretField.get_prep_value"
    ) as mock_get_prep_value:
        mock_get_prep_value.return_value = "gAAAAABnnPiBTtT3tBxzwc0NsELwYKw0mhNvgkMyWAPmMpH8T9PHJio2QyMCvtJTSA94Olbpp0bkFR_uFpjnJ1owzIGo4dqr6Q=="
        instance = models.ModelJSONStatic()
        instance.secret = {"test": "123"}
        instance.save()

    instance = models.ModelJSONStatic.objects.first()
    assert instance.secret == {"test": "123"}

    # Raw SQL to check the value is not versioned
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {models.ModelJSONStatic._meta.db_table}")
        row = cursor.fetchone()
        assert (
            row[1]
            == "gAAAAABnnPiBTtT3tBxzwc0NsELwYKw0mhNvgkMyWAPmMpH8T9PHJio2QyMCvtJTSA94Olbpp0bkFR_uFpjnJ1owzIGo4dqr6Q=="
        )

        MigrateEncryptedCommand().handle()

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {models.ModelJSONStatic._meta.db_table}")
        row = cursor.fetchone()
        assert row[1] != '{"test": "123"}'
        # Decrypt the value to make sure it's valid
        crypter = fernet.Fernet(b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=")
        assert row[1].split("|")[0] == "v1"
        decrypted = crypter.decrypt(row[1].replace("v1|", "").encode("utf-8")).decode(
            "utf-8"
        )
        assert json.loads(decrypted) == {"test": "123"}


def test_json_field_encrypted_key_change() -> None:
    with patch(
        "secrets_fields.fields.SecretField.get_prep_value"
    ) as mock_get_prep_value:
        # encrypted with M2jpxoWkyHXU51ZR0MIEDH0CUkAcivC_TJ-6dpTD29s=
        mock_get_prep_value.return_value = "v1|gAAAAABnnP2i44kjl2dDUask3S-U25o9Sm7A0L28I0unsMolWQgw2SJTEd19ZSDwJuUzLme4Pwu6OOwDmfB2lxRjvN9ZFIieHA=="
        instance = models.ModelJSONStatic()
        instance.secret = {"test": "123"}
        instance.save()
    with patch("secrets_fields.fields.warnings.warn") as mock_warn:
        with pytest.raises(DecryptionException):
            instance = models.ModelJSONStatic.objects.first()
        mock_warn.assert_called_once_with(
            "Decryption of the field failed. Has the key changed?", UserWarning
        )


def test_json_field_encrypted_plaintext_no_migrate() -> None:
    with patch(
        "secrets_fields.fields.SecretField.get_prep_value"
    ) as mock_get_prep_value:
        mock_get_prep_value.return_value = "test"
        instance = models.ModelJSONStatic()
        instance.secret = {"test": "123"}
        instance.save()
    with patch("secrets_fields.fields.warnings.warn") as mock_warn:
        with pytest.raises(DecryptionException):
            instance = models.ModelJSONStatic.objects.first()
        mock_warn.assert_called_once_with(
            "Decryption of the field failed. If you need to migrate a plaintext field to an encrypted form, you can set DJANGO_SECRETS_FIELDS_MIGRATE=True and this field will be migrated using `./manage.py migrate_encrypted`",
            UserWarning,
        )


def test_json_field_existing_null() -> None:
    with patch(
        "secrets_fields.fields.SecretField.get_prep_value"
    ) as mock_get_prep_value:
        mock_get_prep_value.return_value = None
        instance = models.ModelJSONStatic()
        instance.secret = {"test": "123"}
        instance.save()

    instance = models.ModelJSONStatic.objects.first()
    assert instance.secret is None


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
    assert instance.secret.ciphertext == "v1|/path/9a618248b64db62d15b300a07b00580b"

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
def test_model_json_field_mixed_secrets_manager_duplcate() -> None:
    model = mixer.blend(
        models.ModelJSONAWS,
        secret={"test": "supersecret"},
    )
    assert model.secret == {"test": "supersecret"}

    model = mixer.blend(
        models.ModelJSONAWS,
        secret='{"test": "supersecret"}',
    )
    assert model.secret == {"test": "supersecret"}


@mock_aws
@pytest.mark.django_db
def test_model_json_field_mixed_secrets_manager() -> None:
    model = mixer.blend(
        models.ModelJSONAWS,
        secret={"test": "supersecret"},
    )
    assert model.secret == {"test": "supersecret"}

    model = mixer.blend(
        models.ModelJSONAWS,
        secret='{"test": "supersecret1"}',
    )
    assert model.secret == {"test": "supersecret1"}


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
