from django import template
from django.core.serializers import serialize
from django.utils import simplejson
from django.db.models.query import QuerySet

register = template.Library()

@register.simple_tag
def active(request, pattern, active_str="active"):
    import re
    if re.search(pattern, request.path):
        return active_str
    return ''


@register.simple_tag
def sectioncolor(level):
    import colorsys

    (r,g,b) = colorsys.hsv_to_rgb(220.0/360.0, 100.0/100.0, (100.0-(20*level))/100.0)
    return '#%02x%02x%02x' % (r*255,g*255,b*255)


def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return simplejson.dumps(object)

register.filter('jsonify', jsonify)
