from django import template
from datetime import datetime

register = template.Library()

# Return value of a dictionary using a key
@register.filter()
def get_value(dictionary, key):
    return dictionary.get(key)


# Return date value of a timestamp
@register.filter()
def timestamp(timestamp):
    return timestamp.date()
