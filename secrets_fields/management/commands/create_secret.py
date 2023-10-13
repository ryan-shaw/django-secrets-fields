"""
Create secret in AWS Secrets Manager
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from ...util import get_client, get_prefix


class Command(BaseCommand):
    help = "Upload secrets to AWS Secrets Manager"

    def add_arguments(self, parser):
        parser.add_argument("secret_name", help="Name of secret to create")
        parser.add_argument("secret_value", help="Value of secret to create")

    def handle(self, *args, **options):
        prefix = get_prefix()

        role_arn = getattr(settings, "DJANGO_SECRET_FIELDS_AWS_ROLE_ARN_RW", None)
        client = get_client(role_arn=role_arn)

        secret_name = f"{prefix}{options['secret_name']}"
        secret_value = options["secret_value"]
        client.create_secret(
            Name=secret_name,
            SecretString=secret_value,
            Tags=[{"Key": "Managed-By", "Value": "django-secrets-fields"}],
        )
        self.stdout.write(self.style.SUCCESS(f"Created secret {secret_name}"))
