from django.apps import apps
from django.core.management.base import BaseCommand
from secrets_fields.fields import SecretField
from typing import Any


class Command(BaseCommand):
    help = "Migrate existing plaintext fields to encrypted fields"

    def handle(self, *args: Any, **options: Any) -> None:
        total_updated = 0

        # Get all models with a secret field
        for model in apps.get_models():
            secret_fields = [
                field.name
                for field in model._meta.fields
                if isinstance(field, SecretField)
            ]
            if not secret_fields:
                continue

            # Fetch and re-save all model instances

            for instance in model.objects.all():
                # mark the secret_fields list as updated
                instance.save(update_fields=secret_fields)
                total_updated += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated {total_updated} records")
        )
