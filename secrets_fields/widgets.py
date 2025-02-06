import json
from django import forms
from .types import JSON
from typing import Any
from django.utils.safestring import SafeString


class JSONWidget(forms.Textarea):
    def render(
        self,
        name: str,
        value: JSON,
        attrs: dict[str, Any] | None = None,
        renderer: Any = None,
    ) -> SafeString:
        if value is not None:
            value = json.dumps(value, indent=2)
        return super().render(name, value, attrs, renderer)
