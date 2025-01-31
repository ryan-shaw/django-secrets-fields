from django.db import models
from secrets_fields.fields import SecretTextField, SecretJSONField

# Create your models here.


class ModelTextStatic(models.Model):
    secret = SecretTextField(null=True, backend="static")


class ModelJSONStatic(models.Model):
    secret = SecretJSONField(null=True, backend="static")


class ModelTextAWS(models.Model):
    secret = SecretTextField(null=True, backend="aws")


class ModelJSONAWS(models.Model):
    secret = SecretJSONField(null=True, backend="aws")
