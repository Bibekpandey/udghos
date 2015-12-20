from django import template

register = template.Library()

def zipargs(x, y):
    return zip(x,y)


register.filter('zip', zipargs)
