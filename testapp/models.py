from django.db import models
from secrets_fields.fields import SecretTextField

# Create your models here.


class TestModel(models.Model):
    secret = SecretTextField()
