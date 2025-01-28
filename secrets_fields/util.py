import boto3
import uuid
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from .backends.backends import BaseSecretsBackend
from typing import cast


def get_client(role_arn: str | None = None) -> boto3.client:
    """
    Get boto3 client for AWS Secrets Manager
    """
    if role_arn:
        sts_client = boto3.client("sts")
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName=str(uuid.uuid4())
        )
        credentials = assumed_role_object["Credentials"]
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
        return session.client("secretsmanager")
    else:
        return boto3.client("secretsmanager")


def get_prefix() -> str:
    """
    Prefix is defined in settings.py DJANGO_SECRET_FIELDS_PREFIX this function
    returns the prefix
    """
    prefix = getattr(settings, "DJANGO_SECRET_FIELDS_PREFIX", None)
    if prefix is None:
        raise ImproperlyConfigured("DJANGO_SECRET_FIELDS_PREFIX is not set")

    return cast(str, prefix)


def get_backend() -> BaseSecretsBackend:
    """
    Backend is defined in settings.py DJANGO_SECRET_FIELDS_BACKEND this function
    returns the instance of the backend
    """

    backend_str = getattr(settings, "DJANGO_SECRET_FIELDS_BACKEND", None)
    if not backend_str:
        raise ImproperlyConfigured("DJANGO_SECRET_FIELDS_BACKEND is not set")

    return cast(BaseSecretsBackend, import_string(backend_str)())
