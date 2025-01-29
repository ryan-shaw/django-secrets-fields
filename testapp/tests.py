from cryptography import fernet
from django.test import TestCase
from moto import mock_aws
from testapp.models import TestModel
from mixer.backend.django import mixer


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
        self.assertEqual({"test": "supersecret"}, instance.config)
        instance.save()

        self.assertEqual({"test": "supersecret"}, instance.config)

        instance = TestModel.objects.all()[0]
        self.assertEqual({"test": "supersecret"}, instance.config)

    def test_model_json_field_list(self) -> None:
        instance = TestModel()
        instance.config = [1, 2, 3]
        self.assertEqual([1, 2, 3], instance.config)
        instance.save()

        self.assertEqual([1, 2, 3], instance.config)

        instance = TestModel.objects.all()[0]
        self.assertEqual([1, 2, 3], instance.config)

    def test_model_json_field_mixed(self) -> None:
        model = mixer.blend(
            TestModel,
            config={"test": "supersecret"},
            config_aws=None,
            secret_aws=None,
            secret=None,
        )
        self.assertEqual(model.config, {"test": "supersecret"})


@mock_aws
class TestModelSecretsManagerField(TestCase):
    def test_model_text_field(self) -> None:
        instance = TestModel()
        instance.secret_aws = "supersecret"
        instance.save()

        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret_aws.get())
        instance.save()
        self.assertEqual("supersecret", instance.secret_aws.get())
        instance = TestModel.objects.all()[0]
        self.assertEqual("supersecret", instance.secret_aws.get())
        self.assertEqual(
            "/path/9a618248b64db62d15b300a07b00580b", instance.secret_aws.ciphertext
        )

        self.assertEqual("supersecret", instance.secret_aws.plaintext)
        self.assertEqual("supersecret", instance.secret_aws.get())
        self.assertEqual("supersecret", instance.secret_aws.__str__())
        self.assertEqual("supersecret", instance.secret_aws.__repr__())

    def test_model_json_field_dict(self) -> None:
        instance = TestModel()
        instance.config_aws = {"test": "supersecret"}
        instance.save()

        self.assertEqual({"test": "supersecret"}, instance.config_aws)

        instance = TestModel.objects.all()[0]
        self.assertEqual({"test": "supersecret"}, instance.config_aws)

    def test_model_json_field_list(self) -> None:
        instance = TestModel()
        instance.config_aws = [1, 2, 3]
        instance.save()

        self.assertEqual([1, 2, 3], instance.config_aws)

        instance = TestModel.objects.all()[0]
        self.assertEqual([1, 2, 3], instance.config_aws)

    def test_model_json_field_mixed(self) -> None:
        model = mixer.blend(
            TestModel,
            config_aws={"test": "supersecret"},
            config=None,
            secret_aws=None,
            secret=None,
        )
        self.assertEqual(model.config_aws, {"test": "supersecret"})
