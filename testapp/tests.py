import boto3
from secrets_fields.fields import SecretTextField, Secret
from secrets_fields.util import get_backend
from django.test import TestCase
from unittest.mock import patch
from moto import mock_secretsmanager

plaintext = "secret/key/path"


@mock_secretsmanager
class TestSecretTextField(TestCase):
    def setUp(self):
        secretsmanager = boto3.client("secretsmanager", region_name="eu-west-1")
        secretsmanager.create_secret(
            Name=plaintext,
            SecretString=plaintext,
        )

    def test_from_db_value(self):
        secret_value = Secret(plaintext)

        field = SecretTextField()
        result = field.from_db_value(secret_value, None, None)

        assert isinstance(result, Secret)
        assert result.secret == secret_value
        print(result.secret.get(), plaintext)
        assert result.secret.get() == plaintext

    def test_get_prep_value(self):
        secret_value = Secret(plaintext)
        field = SecretTextField()

        prep_value = field.get_prep_value(secret_value)

        assert prep_value == secret_value.ciphertext()

    def test_value_from_object(self):
        secret_value = Secret(plaintext)
        field = SecretTextField()
        field.secret = secret_value
        result = field.value_from_object(field)

        assert result == field.secret.ciphertext()
        assert field.secret.get() == plaintext

    def test_value_to_string(self):
        secret_value = Secret(plaintext)
        field = SecretTextField()
        field.secret = secret_value
        result = field.value_to_string(field)

        assert result == secret_value.ciphertext()
        assert field.secret.get() == plaintext
