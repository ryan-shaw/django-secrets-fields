from django.conf import settings
from django.conf import settings
from django.core.checks import Error, register
from django.apps import apps
from .fields import SecretField

def _has_secret_text_field() -> bool:
    """Check if any model uses SecretTextField."""
    for model in apps.get_models():
        for field in model._meta.get_fields():
            if isinstance(field, SecretField):
                return True
    return False


def check_secret_field_settings(app_configs : dict, **kwargs : dict) -> list[Error]:
    errors = []
    
    if _has_secret_text_field() and not hasattr(settings, "DJANGO_SECRETS_FIELDS"):
        errors.append(
            Error(
                "DJANGO_SECRETS_FIELDS setting is missing.",
                hint="Define DJANGO_SECRETS_FIELDS in your settings if using SecretField.",
                id="secrets_fields.E001",
            )
        )
    
    return errors
