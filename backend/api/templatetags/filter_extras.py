""" This is used only in the partial html file: filter_dynamic.html"""
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Lookup a dict key in the template"""
    return dictionary.get(key)