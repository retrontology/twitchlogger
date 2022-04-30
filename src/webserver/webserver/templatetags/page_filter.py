from django.template import Library

register = Library()

@register.filter(name='pages') 
def pages(last_page):
    return range(last_page+1)