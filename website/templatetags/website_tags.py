from django import template
import os
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

@register.filter
def service_title(value):
    return f"service_{value}_title"  # Adjust if needed

@register.filter
def service_content(value):
    return f"service_{value}_content" 

@register.filter
def service_image(value):
    return f"service_{value}_image"

@register.filter
def get_item(dictionary, key):
    """
    Get value from dictionary by key.

    Example: {{ my_dict|get_item:'my_key' }}
    """
    return dictionary.get(key)

@register.filter
def string_length(value):
    return len(value)


@register.simple_tag(takes_context=True)
def set_local_img_dir(context, prefix):
    """
    Sets the static prefix value in the context.
    """
    context["set_local_img_dir"] = prefix
    return ""

@register.simple_tag(takes_context=True)
def display_media(context, variable):
    """
    A tag that takes context and prints the value of the variable.
    """
    if str(variable).endswith("logo.png"):
        return variable
    
    static_prefix = context.get("set_local_img_dir", "")
    
    full_path_static = f"{static_prefix}/{variable}"
    
    local_path = os.path.join(settings.WEBSITE_MEDIA_ROOT, full_path_static)
    
    print(local_path)
    print(full_path_static)
    
    if os.path.exists(local_path):
        return static(f"website/img/{full_path_static}")
    
    else:
        local_common_path = os.path.join(settings.WEBSITE_MEDIA_ROOT, '__common__')
        
        if os.path.exists(os.path.join(local_common_path, variable)):
            return static(f"website/img/__common__/{variable}")
        
        else:
            return static(f"website/img/__common__/defaults/default_image.png")