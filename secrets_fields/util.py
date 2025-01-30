from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from .backends.backends import BaseSecretsBackend
from typing import cast


def get_config(key: str = "default") -> dict[str, str]:
    """
    Settings are defined in settings.py DJANGO_SECRETS_FIELDS this function
    returns the settings
    """
    config = getattr(settings, "DJANGO_SECRETS_FIELDS", None)
    if config is None:
        raise ImproperlyConfigured("DJANGO_SECRETS_FIELDS is not set")

    return cast(dict[str, str], config.get(key))


def get_backend(key: str = "default") -> BaseSecretsBackend:
    config = get_config(key)
    backend = config.get("backend", None)
    if backend is None:
        raise ImproperlyConfigured("DJANGO_SECRETS_FIELDS['backend'] is not set")

    return cast(BaseSecretsBackend, import_string(backend)(config))
