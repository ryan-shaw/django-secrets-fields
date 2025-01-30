from django.apps import AppConfig
from django.core.checks import register
from .checks import check_secret_field_settings

class DjangoSecretsField(AppConfig):
    name = "secrets_fields"
    verbose_name = "Django Secrets Field"
    
    def ready(self) -> None:
        register()(check_secret_field_settings) # type: ignore[type-var]
