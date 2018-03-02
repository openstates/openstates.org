from django import template

from ..utils import get_legislature_from_state_abbr, states


register = template.Library()


@register.inclusion_tag('public/components/header.html')
def header(state):
    return {
        'state': state,
        'states': states
    }


@register.inclusion_tag('public/components/sources.html')
def sources(state, sources):
    legislature = get_legislature_from_state_abbr(state)
    return {
        'legislature_name': legislature.name,
        'legislature_url': legislature.jurisdiction.url,
        'sources': sources
    }


@register.inclusion_tag('public/components/vote-card.html')
def vote_card(vote_card_object):
    return vote_card_object
