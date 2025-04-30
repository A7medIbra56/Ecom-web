from django import template

register = template.Library()

@register.filter
def has_dashboard_access(user):
    return user.role == "admin" or (user.role == "vendor" and user.vendor.is_approved)
