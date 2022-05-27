
from django import template
from datetime import datetime
register = template.Library()

@register.filter()
def get_value(dictionary, key):
    return dictionary.get(key)

@register.filter()
def timestamp(timestamp):
    return timestamp.date()