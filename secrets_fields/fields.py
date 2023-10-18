"""
Django encrypted model field that fetches the value from AWS Secrets Manager
"""

import time
import django.db.models
from .util import get_backend
from dataclasses import dataclass

backend = get_backend()

TTL = 30

cache = {}


@dataclass
class Cache:
    ttl: int
    value: str


class Secret:
    def __init__(self, secret):
        self.secret = secret

    def get(self):
        obj = cache.get(self.secret, None)
        if obj:
            if obj.ttl > time.time():
                return obj.value
            else:
                del cache[self.secret]

        plaintext = backend.get_secret(self.secret)

        # cache the value
        cache[self.secret] = Cache(ttl=time.time() + TTL, value=plaintext)
        return plaintext

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
