import datetime
from . import static

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def expand_date(date):
    return date + ' 00:00:00' if len(date) == 10 else date

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
                sessions[session.identifier][d] = expand_date(getattr(session, d))

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

def convert_action(a):
    return {
        'date': expand_date(a.date),
        'action': a.description,
        'type': a.classification,
        'related_entities': [],
        'actor': a.organization.classification,
    }

def convert_sponsor(sp):
    return {
        'leg_id': None,         # TODO
        'type': sp.classification,
        'name': sp.entity_name,
    }

def convert_versions(version_list):
    versions = []

    for v in version_list:
        for link in v.links.all():
            versions.append({
                'mimetype': link.media_type,
                'url': link.url,
                'doc_id': '',
                'name': v.note,
            })
    return versions


def convert_bill(b):
    try:
        abstract = b.abstracts.all()[0].abstract
    except IndexError:
        abstract = ""

    # TODO: how do we do this?
    openstates_id = ''

    return {
        'title': b.title,
        'summary': abstract,
        'created_at': b.created_at.strftime(DATE_FORMAT),
        'updated_at': b.updated_at.strftime(DATE_FORMAT),
        'id': openstates_id,
        'all_ids': [openstates_id],
        'chamber': b.from_organization.classification,
        'state': jid_to_abbr(b.legislative_session.jurisdiction_id),
        'session': b.legislative_session.identifier,
        'type': b.classification,
        'bill_id': b.identifier,
        'actions': [convert_action(a) for a in b.actions.all()],
        'sources': [{'url': s.url} for s in b.sources.all()],
        'sponsors': [convert_sponsor(sp) for sp in b.sponsorships.all()],
        'versions': convert_versions(b.versions.all()),
        'documents': convert_versions(b.documents.all()),
        'alternate_titles': [alt.title for alt in b.other_titles.all()],
        'action_dates': {
            'first': expand_date(b.first_action),
            'last': expand_date(b.last_action),
            'passed_upper': None,
            'passed_lower': None,
            'signed': None,
        },
        'alternate_bill_ids': [],
        'subjects': [],
        'companions': [],
    }
