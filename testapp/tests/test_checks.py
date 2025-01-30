import pytest
from django.core.checks import Error
from django.apps.registry import apps
from unittest.mock import patch
from secrets_fields.checks import check_secret_field_settings
from secrets_fields.fields import SecretTextField
from django.db import models
from django.conf import settings


class MockModel(models.Model):
    secret = SecretTextField()

    class Meta:
        app_label = "testapp"


@pytest.fixture
def mock_get_models():
    with patch("secrets_fields.checks.apps.get_models") as mock:
        yield mock


def test_missing_setting_with_secret_field(mock_get_models, monkeypatch):
    mock_get_models.return_value = [MockModel]
    monkeypatch.delattr(settings, "DJANGO_SECRETS_FIELDS", raising=False)
    errors = check_secret_field_settings(apps)
    assert len(errors) == 1
    assert isinstance(errors[0], Error)
    assert errors[0].id == "secrets_fields.E001"


@pytest.mark.parametrize("settings_override", [{"DJANGO_SECRETS_FIELDS": {}}])
def test_present_setting_with_secret_field(
    settings_override, mock_get_models, monkeypatch
):
    monkeypatch.setattr(
        settings, "DJANGO_SECRETS_FIELDS", settings_override["DJANGO_SECRETS_FIELDS"]
    )
    mock_get_models.return_value = [MockModel]
    errors = check_secret_field_settings(apps)
    assert len(errors) == 0


def test_no_secret_field_no_setting(mock_get_models):
    mock_get_models.return_value = []
    errors = check_secret_field_settings(apps)
    assert len(errors) == 0
