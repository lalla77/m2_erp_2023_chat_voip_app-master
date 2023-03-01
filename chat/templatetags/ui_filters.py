from django.template.defaulttags import register
from django import template



# Create your views here.
register = template.Library()

# @register.filter(name='cut')
@register.filter
def get(dictionary, key):
    return dictionary.get(key)