import datetime
from .common import jid_to_abbr


def get_current_role(person):
    today = datetime.date.today().strftime('%Y-%m-%d')
    party = None
    chamber = None
    district = None
    state = None

    # TODO: optimize this query
    for membership in person.memberships.all():
        if not membership.end_date or membership.end_date > today:
            if membership.organization.classification == 'party':
                party = membership.organization.name
            elif membership.organization.classification in ('upper', 'lower', 'legislature'):
                chamber = membership.organization.classification
                district = membership.post.label
                state = jid_to_abbr(membership.organization.jurisdiction_id)

    return {'party': party, 'chamber': chamber, 'state': state, 'district': district}
