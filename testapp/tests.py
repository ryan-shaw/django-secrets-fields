import boto3
from secrets_fields.fields import SecretTextField, Secret
from django.test import TestCase
from moto import mock_aws
from unittest import mock
from unittest.mock import patch
from django.test import override_settings
from testapp.models import TestModel


@mock_aws
@override_settings(
    DJANGO_SECRET_FIELDS_BACKEND="secrets_fields.backends.secretsmanager.SecretsManagerBackend"
)
class TestSecretsManagerField(TestCase):
    keypath = "secret/key/path"
    plaintext = "supersecret"

    def setUp(self) -> None:
        secretsmanager = boto3.client("secretsmanager", region_name="eu-west-1")
        secretsmanager.create_secret(
            Name=self.keypath,
            SecretString=self.plaintext,
        )

    def test_from_db_value(self) -> None:
        field = SecretTextField()
        result = field.from_db_value(self.keypath, None, None)

        assert isinstance(result, Secret)
        assert result.ciphertext == self.keypath
        assert result.get() == self.plaintext

    def test_get_prep_value(self) -> None:
        secret_value = Secret(self.plaintext, {})
        field = SecretTextField()

        prep_value = field.get_prep_value(secret_value)

        assert prep_value == secret_value.ciphertext


@override_settings(
    DJANGO_SECRET_FIELDS_BACKEND="secrets_fields.backends.encrypted.EncryptedBackend",
    DJANGO_SECRET_FIELDS_ENCRYPTION_KEY=b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=",
)
class TestEncryptedField(TestCase):
    ciphertext = "gAAAAABnmKOCAAAAAAAAAAAAAAAAAAAAAAtM8UZYN5Z054Q51w9UInjrALwHWAkUGe0CDchh7T1gV9v9hvsu8Vpp_GXO-VPMfA=="
    plaintext = "secret/key/path"

    def test_from_db_value(self) -> None:
        # from db returns the value from the DB so needs decrypting
        field = SecretTextField()
        result = field.from_db_value(self.ciphertext, None, None)

        assert isinstance(result, Secret)
        assert result.ciphertext == self.ciphertext
        assert result.get() == self.plaintext

    @patch("os.urandom", return_value=b"\x00" * 16)
    def test_get_prep_value(self, _ : mock.Mock) -> None:
        # Needs to encrypt the object to store in the database
        secret_value = Secret(self.plaintext, {})
        field = SecretTextField()

        prep_value = field.get_prep_value(secret_value)

        assert prep_value == secret_value.ciphertext


@override_settings(
    DJANGO_SECRET_FIELDS_BACKEND="secrets_fields.backends.encrypted.EncryptedBackend",
    DJANGO_SECRET_FIELDS_ENCRYPTION_KEY=b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=",
)
class TestModelEncryptedField(TestCase):
    def test_model_field_encryptedfield(self) -> None:
        instance = TestModel()
        instance.secret = "supersecret"
        instance.save()

        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret.get())
        instance.save()
        self.assertEqual("supersecret", instance.secret.get())
        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret.get())


@mock_aws
@override_settings(
    DJANGO_SECRET_FIELDS_BACKEND="secrets_fields.backends.secretsmanager.SecretsManagerBackend"
)
class TestModelSecretsManagerField(TestCase):
    def test_model_field_secretsmanager(self) -> None:
        secretsmanager = boto3.client("secretsmanager", region_name="eu-west-1")
        secretsmanager.create_secret(
            Name="/path/",
            SecretString="supersecret",
        )

        instance = TestModel()
        instance.secret = Secret("/path/", {})
        instance.save()

        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret.get())
        instance.save()
        self.assertEqual("supersecret", instance.secret.get())
        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret.get())
        self.assertEqual("/path/", instance.secret.ciphertext)
