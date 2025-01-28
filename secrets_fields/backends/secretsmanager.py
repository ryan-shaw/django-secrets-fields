try:
    import boto3
except ImportError:
    raise ImportError("boto3 is required for AWS Secrets Manager backend - pip install django-secrets-fields[aws]")
from .backends import BaseSecretsBackend
from django.conf import settings
from typing import cast



class SecretsManagerBackend(BaseSecretsBackend):
    """AWS Secrets Manager backend

    Uses AWS Secrets Manager to store secrets
    """

    @property
    def client_ro(self) -> boto3.client:
        return _get_client(
            role_arn=getattr(settings, "DJANGO_SECRET_FIELDS_AWS_ROLE_ARN_RO", None)
        )

    @property
    def client_rw(self) -> boto3.client:
        return _get_client(
            role_arn=getattr(settings, "DJANGO_SECRET_FIELDS_AWS_ROLE_ARN_RW", None)
        )

    def get_ciphertext(self, secret_value: str) -> str:
        return secret_value

    def create_secret(self, *args : list) -> str:
        """Create secret using the backend

        Returns:
            str: secret_name
        """
        self.client_rw.create_secret(
            Name=args[0],
            SecretString=args[1],
            Tags=[{"Key": "Managed-By", "Value": "django-secrets-fields"}],
        )
        return cast(str, args[0])

    def get_secret(self, secret_name: str) -> str:
        """Get secret from backend

        Args:
            secret_name (str): name of the secret

        Returns:
            str: plaintext secret
        """
        return cast(str, self.client_ro.get_secret_value(SecretId=secret_name)["SecretString"])


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
