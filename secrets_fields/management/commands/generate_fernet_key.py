from cryptography.fernet import Fernet
from django.core.management.base import BaseCommand
from typing import Any


class Command(BaseCommand):
    help = "Generate a Fernet encryption key"

    def handle(self, *args: Any, **options: Any) -> None:
        # Generate a Fernet key
        key = Fernet.generate_key()

        # Decode the key to make it human-readable
        key_str = key.decode("utf-8")

        self.stdout.write(self.style.SUCCESS(f"Your Fernet key: {key_str}"))
        self.stdout.write(
            "Store this key in a safe place, such as your environment variables or a secrets manager."
        )
