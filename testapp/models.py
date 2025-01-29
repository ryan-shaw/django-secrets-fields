from django.db import models
from secrets_fields.fields import SecretTextField, SecretJSONField

# Create your models here.


class TestModel(models.Model):
    secret = SecretTextField(null=True)
    config = SecretJSONField(null=True)
