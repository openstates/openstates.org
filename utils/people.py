import datetime
from django.utils.text import slugify
from .common import jid_to_abbr, encode_uuid


def get_current_role(person):
    today = datetime.date.today().strftime('%Y-%m-%d')
    party = None
    post = None
    state = None

    # TODO: optimize this query
    for membership in person.memberships.all():
        if not membership.end_date or membership.end_date > today:
            if membership.organization.classification == 'party':
                party = membership.organization.name
            elif membership.organization.classification in ('upper', 'lower', 'legislature'):
                chamber = membership.organization.classification
                state = jid_to_abbr(membership.organization.jurisdiction_id)
                post = membership.post

    return {'party': party, 'chamber': chamber, 'state': state,
            'district': post.label, 'division_id': post.division_id, 'role': post.role,
            }


def pretty_url(person):
    return f'/public/person/{slugify(person.name)}-{encode_uuid(person.id)}'
