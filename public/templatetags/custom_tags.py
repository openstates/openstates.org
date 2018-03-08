from django import template
import us

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
def vote_card(vote):
    # Model needs to be wrapped in a dict, per custom-tag requirements
    return {'vote': vote}


@register.inclusion_tag('public/components/action-card.html')
def action_card(action):
    # Model needs to be wrapped in a dict, per custom-tag requirements
    return {'action': action}


@register.filter()
def state_name(state_abbr):
    return us.states.lookup(state_abbr).name
