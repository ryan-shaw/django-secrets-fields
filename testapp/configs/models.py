from django.db import models
from secrets_fields.fields import SecretTextField, SecretJSONField

# Create your models here.


class TestModel(models.Model):
    secret = SecretTextField(null=True, backend="static")
    config = SecretJSONField(null=True, backend="static")
    secret_aws = SecretTextField(null=True, backend="aws")
    config_aws = SecretJSONField(null=True, backend="aws")
