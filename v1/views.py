import datetime
from django.shortcuts import render
from django.http import JsonResponse
from opencivicdata.legislative.models import Bill
from opencivicdata.core.models import Jurisdiction

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# these are to mimic empty committee/event responses

def empty_list(request):
    return JsonResponse([], safe=False)


def item_404(request, id):
    return JsonResponse("Not Found", safe=False, status=404)


def _convert_jurisdiction(j):
    return j.split(':')[-1].split('/')[0]


def _convert_bill(b):
    return {
        'title': b.title,
        'created_at': b.created_at.strftime(DATE_FORMAT),
        'updated_at': b.updated_at.strftime(DATE_FORMAT),
        'id': '',       # TODO
        'chamber': b.from_organization.classification,
        'state': _convert_jurisdiction(b.legislative_session.jurisdiction_id),
        'session': b.legislative_session.identifier,
        'type': b.classification,
        'subjects': [],
        'bill_id': b.identifier,
    }



def _abbr_to_jurisdiction_id(abbr):
    if abbr == 'dc':
        return 'ocd-jurisdiction/country:us/district:dc/government'
    elif abbr == 'pr':
        return 'ocd-jurisdiction/country:us/territory:pr/government'
    else:
        return f'ocd-jurisdiction/country:us/state:{abbr}/government'


def _state_metadata(abbr, jurisdiction):
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
        'abbreviation': abbr,
        'legislature_name': orgs['legislature'].name,
        'legislature_url': jurisdiction.url,
        'chambers': chambers,
        'session_details': sessions,
        'latest_update': jurisdiction.runs.latest('start_time').start_time.strftime(
            '%Y-%m-%d %H:%M:%S'
        ),
        # 'terms': [], # TODO
        # 'capitol_timezone': 'America/New_York',    # TODO

        # static content
        'feature_flags': [],
        'latest_csv_date': '1970-01-01 00:00:00',
        'latest_csv_url': 'https://openstates.org/downloads/',
        'latest_json_date': '1970-01-01 00:00:00',
        'latest_json_url': 'https://openstates.org/downloads/',
    }


def state_metadata(request, abbr):
    jid = _abbr_to_jurisdiction_id(abbr)
    jurisdiction = Jurisdiction.objects.get(pk=jid)
    return JsonResponse(_state_metadata(abbr, jurisdiction))


def all_metadata(request):
    return [_state_metadata(_jid_to_abbr(j.id), j) for j in Jurisdiction.objects.all()]


def bill_list(request):
    query = request.GET.get('q')
    state = request.GET.get('state')
    search_window = request.GET.get('search_window')
    since = request.GET.get('since')
    last_action_since = request.GET.get('since')
    sponsor_id = request.GET.get('sponsor_id')
    classification = request.GET.get('type')

    # deprecate subjects, status?

    bills = Bill.objects.all()

    # TODO: sorting

    return JsonResponse([_convert_bill(b) for b in Bill.objects.all()[:100]], 
                        safe=False)
