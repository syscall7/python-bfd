from django import template

register = template.Library()

@register.simple_tag
def active(request, pattern, active_str="active"):
    import re
    if re.search(pattern, request.path):
        return active_str
    return ''