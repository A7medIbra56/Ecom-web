from django import template
from django.conf import settings
from slippers.templatetags.slippers import register_components

register = template.Library()

register_components(
    {
        "container": "components/container.html",
        "form": "components/form.html",
        "form_field": "components/form_field.html",
    },
    register,
)
