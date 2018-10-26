from django.http import JsonResponse
from opencivicdata.legislative.models import Bill
from opencivicdata.core.models import Jurisdiction
from . import utils


# these are to mimic empty committee/event responses

def empty_list(request):
    return JsonResponse([], safe=False)


def item_404(request, id):
    return JsonResponse("Not Found", safe=False, status=404)


def state_metadata(request, abbr):
    jid = utils.abbr_to_jid(abbr)
    jurisdiction = Jurisdiction.objects.get(pk=jid)
    return JsonResponse(utils.state_metadata(abbr, jurisdiction))


def all_metadata(request):
    return JsonResponse(
        [utils.state_metadata(utils.jid_to_abbr(j.id), j) for j in Jurisdiction.objects.all()],
        safe=False
    )


def bill_list(request):
    state = request.GET.get('state')
    chamber = request.GET.get('chamber')
    bill_id = request.GET.get('bill_id')
    query = request.GET.get('q')
    search_window = request.GET.get('search_window', 'all')
    updated_since = request.GET.get('updated_since')

    # page, per_page, sort

    bills = Bill.objects.all()
    if state:
        jid = utils.abbr_to_jid(state)
        bills = bills.filter(legislative_session__jurisdiction_id=jid)
    if chamber:
        if state in ('ne', 'dc') and chamber == 'upper':
            chamber = 'legislature'
        bills = bills.filter(from_organization__classification=chamber)
    if query:
        bills = bills.filter(title__icontains=query)
    if updated_since:
        bills = bills.filter(updated_at__lt=updated_since)
    if bill_id:
        bills = bills.filter(identifier=bill_id)

    # TODO: finish search window
    if search_window == 'session':
        pass    # session__identifier=current_session
    elif search_window == 'term':
        pass    # session__identifier__in=current_term_sessions
        # simple_args['_current_term'] = True
    elif search_window.startswith('session:'):
        bills.filter(session__identifier=search_window.split('session:')[1])
    elif search_window != 'all':
        raise ValueError('invalid search_window. valid choices are "term", "session", "all"')

    # TODO: sorting & pagination

    return JsonResponse([utils.convert_bill(b) for b in Bill.objects.all()[:100]], 
                        safe=False)
