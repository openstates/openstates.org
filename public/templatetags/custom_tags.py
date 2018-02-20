from django import template


register = template.Library()


@register.inclusion_tag('public/components/sources.html')
def sources(sources_object):
    return sources_object
