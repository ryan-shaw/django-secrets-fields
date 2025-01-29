"""
Django encrypted model field that fetches the value from AWS Secrets Manager
"""

import json
import django.db.models
from .util import get_backend
from dataclasses import dataclass
from typing import Any, TypeAlias, TypeVar, Type, cast, Generic

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


TTL = 30


@dataclass
class Cache:
    ttl: float
    value: str


cache: dict[str, Cache] = {}

T = TypeVar("T")


class SecretBase(Generic[T]):
    def __init__(
        self,
        *,
        backend: str = "default",
        plaintext: T | None = None,
        ciphertext: str | None = None,
    ):
        self.ciphertext = ciphertext
        self._plaintext = plaintext
        self._backend = get_backend(backend)
        if not self.ciphertext and self._plaintext:
            self.ciphertext = self._backend.encrypt(
                self.prepare_ciphertext(self._plaintext)
            )

    def prepare_ciphertext(self, value: T) -> str:
        """Prepare the plaintext for encryption"""
        return cast(str, value)

    def to_python(self, value: Any) -> T:
        """Convert the decrypted ciphertext to a python object"""
        return cast(T, value)

    @property
    def plaintext(self) -> T | None:
        return self.get()

    def __str__(self) -> str:
        return cast(str, self.get())

    def __repr__(self) -> str:
        return cast(str, self.get())

    def get(self) -> T | None:
        if self.ciphertext is None:
            return None
        return self.to_python(self._backend.decrypt(self.ciphertext))


class SecretText(SecretBase[str]):
    pass


TF = TypeVar("TF", bound=SecretBase[Any])


class SecretField(django.db.models.TextField, Generic[TF]):
    attname: str

    def __init__(
        self, secret_type: Type[TF], backend: str = "default", *args: Any, **kwargs: Any
    ):
        self.secret_type = secret_type
        self.backend = backend
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value: TF | str | None) -> str | None:
        # if not self.secret_type we need to convert to self.secret_type and encrypt it
        if value is None:
            return None
        if not isinstance(value, SecretBase):
            value = self.secret_type(plaintext=value, backend=self.backend)
        return value.ciphertext

    def get_internal_type(self) -> str:
        return "TextField"


class SecretTextField(SecretField[SecretText]):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(SecretText, *args, **kwargs)

    def from_db_value(
        self, ciphertext: str, expression: str | None, connection: Any
    ) -> SecretText:
        return self.secret_type(ciphertext=ciphertext, backend=self.backend)


class SecretJSON(SecretBase[JSON]):
    def prepare_ciphertext(self, value: JSON) -> str:
        return json.dumps(value)

    def to_python(self, value: str) -> JSON:
        return cast(JSON, json.loads(value))

    # def __dict__(self) -> JSON:
    #     return self.get()


class SecretJSONField(SecretField[SecretJSON]):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(SecretJSON, *args, **kwargs)

    def from_db_value(
        self, ciphertext: str, expression: str | None, connection: Any
    ) -> Any:
        return self.secret_type(ciphertext=ciphertext, backend=self.backend).get()

    def to_python(self, value: str | JSON | None) -> JSON | None:
        if isinstance(value, str):
            return cast(JSON, json.loads(value))
        return value

    def get_internal_type(self) -> str:
        return "TextField"
