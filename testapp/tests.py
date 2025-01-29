from cryptography import fernet
from django.test import TestCase
from moto import mock_aws
from django.test import override_settings
from testapp.models import TestModel


@override_settings(
    DJANGO_SECRET_FIELDS={
        "backend": "secrets_fields.backends.encrypted.EncryptedBackend",
        "encryption_key": b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=",
    }
)
class TestModelEncryptedField(TestCase):
    def test_model_text_field(self) -> None:
        instance = TestModel()
        instance.secret = "supersecret"
        instance.save()

        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret.get())
        instance.save()
        self.assertEqual("supersecret", instance.secret.get())
        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret.get())

        crypter = fernet.Fernet(b"5_SgmNvlc9aNe1qePC2VdkJHE9fEUYN4xLVUoVZ6IbM=")
        ciphertext = instance.secret.ciphertext
        decrypted = crypter.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        self.assertEqual("supersecret", decrypted)

        self.assertEqual("supersecret", instance.secret.plaintext)
        self.assertEqual("supersecret", instance.secret.get())
        self.assertEqual("supersecret", instance.secret.__str__())
        self.assertEqual("supersecret", instance.secret.__repr__())

    def test_model_json_field_dict(self) -> None:
        instance = TestModel()
        instance.config = {"test": "supersecret"}
        instance.save()

        self.assertEqual({"test": "supersecret"}, instance.config)

        instance = TestModel.objects.all()[0]
        self.assertEqual({"test": "supersecret"}, instance.config)

    def test_model_json_field_list(self) -> None:
        instance = TestModel()
        instance.config = [1, 2, 3]
        instance.save()

        self.assertEqual([1, 2, 3], instance.config)

        instance = TestModel.objects.all()[0]
        self.assertEqual([1, 2, 3], instance.config)


@mock_aws
@override_settings(
    DJANGO_SECRET_FIELDS={
        "backend": "secrets_fields.backends.secretsmanager.SecretsManagerBackend",
        "prefix": "/path/",
    }
)
class TestModelSecretsManagerField(TestCase):
    def test_model_text_field(self) -> None:
        instance = TestModel()
        instance.secret = "supersecret"
        instance.save()

        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret.get())
        instance.save()
        self.assertEqual("supersecret", instance.secret.get())
        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret.get())
        self.assertEqual(
            "/path/9a618248b64db62d15b300a07b00580b", instance.secret.ciphertext
        )

        self.assertEqual("supersecret", instance.secret.plaintext)
        self.assertEqual("supersecret", instance.secret.get())
        self.assertEqual("supersecret", instance.secret.__str__())
        self.assertEqual("supersecret", instance.secret.__repr__())

    def test_model_json_field_dict(self) -> None:
        instance = TestModel()
        instance.config = {"test": "supersecret"}
        instance.save()

        self.assertEqual({"test": "supersecret"}, instance.config)

        instance = TestModel.objects.all()[0]
        self.assertEqual({"test": "supersecret"}, instance.config)

    def test_model_json_field_list(self) -> None:
        instance = TestModel()
        instance.config = [1, 2, 3]
        instance.save()

        self.assertEqual([1, 2, 3], instance.config)

        instance = TestModel.objects.all()[0]
        self.assertEqual([1, 2, 3], instance.config)
