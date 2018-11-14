import us
import uuid
import base62
from django.utils.text import slugify
from opencivicdata.core.models import Person
from opencivicdata.legislative.models import Bill

# Metadata for states that are available in the platform
states = sorted(us.STATES + [us.states.PR], key=lambda s: s.name)


def jid_to_abbr(j):
    return j.split(':')[-1].split('/')[0]


def abbr_to_jid(abbr):
    if abbr == 'dc':
        return 'ocd-jurisdiction/country:us/district:dc/government'
    elif abbr == 'pr':
        return 'ocd-jurisdiction/country:us/territory:pr/government'
    else:
        return f'ocd-jurisdiction/country:us/state:{abbr}/government'


def encode_uuid(id):
    uuid_portion = str(id).split('/')[1]
    as_int = uuid.UUID(uuid_portion).int
    return base62.encode(as_int)


def decode_uuid(id, type='person'):
    decoded = uuid.UUID(int=base62.decode(id))
    return f'ocd-{type}/{decoded}'


def pretty_url(obj):
    if isinstance(obj, Person):
        return f'/public/person/{slugify(obj.name)}-{encode_uuid(obj.id)}'
    elif isinstance(obj, Bill):
        state = jid_to_abbr(obj.legislative_session.jurisdiction_id)
        identifier = obj.identifier.replace(' ', '')
        return f'/public/{state}/bills/{obj.legislative_session.identifier}/{identifier}'
