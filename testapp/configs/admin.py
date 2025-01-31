# Register your models here.

from django.contrib import admin
from .models import ModelJSONAWS, ModelJSONStatic, ModelTextAWS, ModelTextStatic

admin.site.register(ModelTextStatic)
admin.site.register(ModelJSONStatic)
admin.site.register(ModelTextAWS)
admin.site.register(ModelJSONAWS)
