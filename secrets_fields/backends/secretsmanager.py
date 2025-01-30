try:
    import boto3
except ImportError:
    raise ImportError(
        "boto3 is required for AWS Secrets Manager backend - pip install django-secrets-fields[aws]"
    )
import hashlib
from .backends import BaseSecretsBackend
from django.conf import settings
from typing import cast


class SecretsManagerBackend(BaseSecretsBackend):
    """AWS Secrets Manager backend

    Uses AWS Secrets Manager to store secrets
    """

    @property
    def client_ro(self) -> boto3.client:
        role_arn_ro = self.config.get("role_arn_ro", None)
        return _get_client(
            role_arn=role_arn_ro,
        )

    @property
    def client_rw(self) -> boto3.client:
        role_rw = self.config.get("role_arn_rw", None)
        return _get_client(
            role_arn=role_rw,
        )

    def _generate_name(self, plaintext: str) -> str:
        """
        Hash the plaintext to generate the name for the secret
        """
        prefix = self.config.get("prefix", None)
        if not prefix:
            raise ValueError("DJANGO_SECRETS_FIELDS['backend']['prefix'] must be set")
        return cast(str, prefix + hashlib.md5(plaintext.encode("utf-8")).hexdigest())

    def encrypt(self, plaintext: str) -> str:
        """Create secret using the backend

        Returns:
            str: secret path
        """
        name = self._generate_name(plaintext)
        self.client_rw.create_secret(
            Name=name,
            SecretString=plaintext,
            Tags=[{"Key": "Managed-By", "Value": "django-secrets-fields"}],
        )
        return name

    def decrypt(self, ciphertext: str) -> str:
        """Get secret from backend

        Args:
            ciphertext (str): the path of the secret in AWS Secrets Manager

        Returns:
            str: plaintext secret
        """
        return cast(
            str, self.client_ro.get_secret_value(SecretId=ciphertext)["SecretString"]
        )


def _get_client(role_arn: str | None = None) -> boto3.client:
    """
    Get boto3 client for AWS Secrets Manager
    """
    if role_arn:
        sts_client = boto3.client("sts")
        assumed_role_object = sts_client.assume_role(RoleArn=role_arn)
        credentials = assumed_role_object["Credentials"]
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
        return session.client("secretsmanager")
    else:
        return boto3.client("secretsmanager")
