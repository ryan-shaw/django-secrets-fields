"""
Django encrypted model field that fetches the value from AWS Secrets Manager
"""

import django.db.models
from django.conf import settings
from .util import get_client


class SecretsManagerMixin(object):
    def to_python(self, value: str):
        if value is None:
            return value

        # fetch from secrets manager
        role_arn = getattr(settings, "DJANGO_SECRET_FIELDS_AWS_ROLE_ARN_RO", None)
        client = get_client(role_arn=role_arn)
        secret = client.get_secret_value(SecretId=value)

        return super(SecretsManagerMixin, self).to_python(secret["SecretString"])

    def get_internal_type(self):
        return "TextField"


class SecretTextField(SecretsManagerMixin, django.db.models.TextField):
    pass
