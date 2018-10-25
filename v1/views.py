import datetime
from django.shortcuts import render
from django.http import JsonResponse
from opencivicdata.legislative.models import Bill

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


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
