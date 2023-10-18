import boto3
from .backends import BaseSecretsBackend
from django.conf import settings


class SecretsManagerBackend(BaseSecretsBackend):
    """AWS Secrets Manager backend

    Uses AWS Secrets Manager to store secrets
    """

    @property
    def client_ro(self):
        return _get_client(
            role_arn=getattr(settings, "DJANGO_SECRET_FIELDS_AWS_ROLE_ARN_RO", None)
        )

    @property
    def client_rw(self):
        return _get_client(
            role_arn=getattr(settings, "DJANGO_SECRET_FIELDS_AWS_ROLE_ARN_RW", None)
        )

    def create_secret(self, secret_name: str, secret_value: str):
        """Create secret using the backend

        Args:
            secret_name (str): name of the secret
            secret_value (str): plaintext secret
        """
        self.client_rw.create_secret(
            Name=secret_name,
            SecretString=secret_value,
            Tags=[{"Key": "Managed-By", "Value": "django-secrets-fields"}],
        )

    def get_secret(self, secret_name: str) -> str:
        """Get secret from backend

        Args:
            secret_name (str): name of the secret

        Returns:
            str: plaintext secret
        """
        return self.client_ro.get_secret_value(SecretId=secret_name)["SecretString"]


def _get_client(role_arn: str = None) -> boto3.client:
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
