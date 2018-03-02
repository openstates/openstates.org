from django.db.models import Q
from opencivicdata.core.models import Organization
import us


# List of jurisdictions are available in the platform
states = us.STATES + [us.states.PR]


def get_legislature_from_state_abbr(state):
    jurisdiction_id_fragment = '/territory:dc' if state == 'pr' else \
        '/district:dc' if state == 'dc' else \
        '/state:{}'.format(state)
    legislature = Organization.objects.get(
        classification='legislature',
        jurisdiction__id__contains=jurisdiction_id_fragment
    )
    return legislature


def get_legislative_post(person):
    return person.memberships.get(
        Q(organization__classification='legislature') |
        Q(organization__classification='lower') |
        Q(organization__classification='upper')
    ).post
