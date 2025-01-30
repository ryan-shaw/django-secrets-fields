import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from secrets_fields.util import get_config, get_backend


def test_get_config_missing_setting(monkeypatch):
    monkeypatch.delattr(settings, "DJANGO_SECRETS_FIELDS", raising=False)
    with pytest.raises(ImproperlyConfigured, match="DJANGO_SECRETS_FIELDS is not set"):
        get_config()


def test_get_config_valid(monkeypatch):
    monkeypatch.setattr(
        settings,
        "DJANGO_SECRETS_FIELDS",
        {"default": {"backend": "myapp.backends.backends.MockBackend"}},
    )
    config = get_config()
    assert config == {"backend": "myapp.backends.backends.MockBackend"}


def test_get_backend_missing_backend(monkeypatch):
    monkeypatch.setattr(settings, "DJANGO_SECRETS_FIELDS", {"default": {}})
    with pytest.raises(
        ImproperlyConfigured, match="DJANGO_SECRETS_FIELDS\['backend'\] is not set"
    ):
        get_backend()
