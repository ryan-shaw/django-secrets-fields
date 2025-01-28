"""
Django encrypted model field that fetches the value from AWS Secrets Manager
"""

import time
import django.db.models
from .util import get_backend
from dataclasses import dataclass
from typing import Any, cast

TTL = 30

@dataclass
class Cache:
    ttl: float
    value: str

cache : dict[str, Cache] = {}


class Secret:
    def __init__(self, ciphertext : str, kwargs : dict[str, Any] | None = None):
        if kwargs is None:
            kwargs = {}
        self.ciphertext = ciphertext
        self.kwargs = kwargs

    def encrypt(self, plaintext : str) -> str:
        backend = get_backend()
        return backend.create_secret(plaintext)

    def get(self) -> str | None:
        if self.ciphertext == "":
            return None
        obj = cache.get(self.ciphertext, None)
        if obj:
            if obj.ttl > time.time():
                return obj.value
            else:
                del cache[self.ciphertext]

        backend = get_backend()
        plaintext = backend.get_secret(self.ciphertext)

        # cache the value
        cache[self.ciphertext] = Cache(ttl=time.time() + TTL, value=plaintext)
        return plaintext


class SecretsManagerMixin(object):
    
    attname : str
    
    def __init__(self, *args : list, **kwargs : dict[str, Any]) -> None:
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)

    def from_db_value(self, ciphertext: str, expression : str | None, connection : Any) -> Secret:
        return Secret(ciphertext, self.kwargs).get()

    def get_db_prep_value(self, value : str | Secret, connection : Any, prepared : bool = False) -> str | None:
        if isinstance(value, Secret):
            return value.ciphertext
        return Secret("", self.kwargs).encrypt(value)

    def get_prep_value(self, ciphertext : str | Secret) -> str:
        if isinstance(ciphertext, Secret):
            return ciphertext.ciphertext
        return ciphertext

    def value_from_object(self, obj : Any) -> str:
        # Get the ciphertext before serialisation
        attr = getattr(obj, self.attname)
        return cast(str, attr.ciphertext)

    def value_to_string(self, obj: django.db.models.Model) -> str:
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def get_internal_type(self) -> str:
        return "TextField"


class SecretTextField(SecretsManagerMixin, django.db.models.TextField):
    pass
