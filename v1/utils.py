import datetime
from . import static

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def jid_to_abbr(j):
    return j.split(':')[-1].split('/')[0]


def abbr_to_jid(abbr):
    if abbr == 'dc':
        return 'ocd-jurisdiction/country:us/district:dc/government'
    elif abbr == 'pr':
        return 'ocd-jurisdiction/country:us/territory:pr/government'
    else:
        return f'ocd-jurisdiction/country:us/state:{abbr}/government'


def state_metadata(abbr, jurisdiction):
    orgs = {
        o.classification: o for o in
        jurisdiction.organizations.filter(classification__in=('legislature', 'upper', 'lower'))
    }

    chambers = {}
    for chamber in ('upper', 'lower'):
        if chamber in orgs:
            role = orgs[chamber].posts.all()[0].role
            chambers[chamber] = {
                'name': orgs[chamber].name,
                'title': role,
            }

    sessions = {}
    for session in jurisdiction.legislative_sessions.all():
        sessions[session.identifier] = {
            'display_name': session.name,
            'type': session.classification,
        }
        for d in ('start_date', 'end_date'):
            if getattr(session, d):
                sessions[session.identifier][d] = getattr(session, d) + ' 00:00:00'

    return {
        'id': abbr,
        'name': jurisdiction.name,
        'abbreviation': abbr,
        'legislature_name': orgs['legislature'].name,
        'legislature_url': jurisdiction.url,
        'chambers': chambers,
        'session_details': sessions,
        'latest_update': jurisdiction.runs.latest('start_time').start_time.strftime(DATE_FORMAT),
        'capitol_timezone': static.TIMEZONES[abbr],
        'terms': static.TERMS[abbr],
        'feature_flags': [],
        'latest_csv_date': '1970-01-01 00:00:00',
        'latest_csv_url': 'https://openstates.org/downloads/',
        'latest_json_date': '1970-01-01 00:00:00',
        'latest_json_url': 'https://openstates.org/downloads/',
    }


def convert_bill(b):
    return {
        'title': b.title,
        'created_at': b.created_at.strftime(DATE_FORMAT),
        'updated_at': b.updated_at.strftime(DATE_FORMAT),
        'id': '',       # TODO
        'chamber': b.from_organization.classification,
        'state': jid_to_abbr(b.legislative_session.jurisdiction_id),
        'session': b.legislative_session.identifier,
        'type': b.classification,
        'subjects': [],
        'bill_id': b.identifier,
    }
