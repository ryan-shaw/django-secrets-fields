"""
Django encrypted model field that fetches the value from AWS Secrets Manager
"""

import django.db.models
from django import forms
from django.conf import settings
from .util import get_client


class Secret:
    def __init__(self, secret):
        self.secret = secret

    def get(self):
        # fetch from secrets manager
        role_arn = getattr(settings, "DJANGO_SECRET_FIELDS_AWS_ROLE_ARN_RO", None)
        client = get_client(role_arn=role_arn)
        try:
            secret = client.get_secret_value(SecretId=self.secret)
        except Exception as e:
            return str(e)

        return secret["SecretString"]

    def ciphertext(self):
        return self.secret


class SecretsManagerMixin(object):
    def from_db_value(self, value, expression, connection):
        return Secret(value)

    def get_prep_value(self, value):
        if isinstance(value, Secret):
            return value.ciphertext()
        return value

    def value_from_object(self, obj):
        return obj.secret.ciphertext()

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def get_internal_type(self):
        return "TextField"


class SecretTextField(SecretsManagerMixin, django.db.models.TextField):
    pass
