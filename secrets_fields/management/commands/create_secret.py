"""
Create secret in AWS Secrets Manager
"""

from django.core.management.base import BaseCommand
from ...util import get_prefix, get_backend
from typing import Any


class Command(BaseCommand):
    help = "Upload secrets to AWS Secrets Manager"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("secret_name", help="Name of secret to create")
        parser.add_argument("secret_value", help="Value of secret to create")

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        prefix = get_prefix()
        backend = get_backend()

        secret_name = f"{prefix}{options['secret_name']}"
        secret_value = options["secret_value"]
        backend.create_secret(secret_name, secret_value)
        self.stdout.write(self.style.SUCCESS(f"Created secret {secret_name}"))
