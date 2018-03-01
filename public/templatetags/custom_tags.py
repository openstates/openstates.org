from django import template


register = template.Library()


@register.inclusion_tag('public/components/sources.html')
def sources(sources_object):
    return sources_object


@register.inclusion_tag('public/components/vote-card.html')
def vote_card(vote_card_object):
    return vote_card_object
