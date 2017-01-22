from django import template

register = template.Library()

def subtract(x, y):
    return x - y

register.filter('subtract', subtract)
