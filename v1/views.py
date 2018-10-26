from django.http import JsonResponse
from django.db.models import Subquery, OuterRef, Max
from opencivicdata.legislative.models import Bill, LegislativeSession
from opencivicdata.core.models import Jurisdiction
from . import utils, static


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
    sort = request.GET.get('sort', 'last')

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
        bills = bills.filter(updated_at__gt=updated_since)
    if bill_id:
        bills = bills.filter(identifier=bill_id)

    # search_window only ever really worked w/ state- and judging by analytics that's how
    # it was used in every case
    if state:
        if search_window == 'session':
            latest_session = LegislativeSession.objects.filter(
                jurisdiction_id=jid
            ).order_by('-start_date').values_list('identifier', flat=True)[0]
            bills = bills.filter(legislative_session__identifier=latest_session)
        elif search_window == 'term':
            latest_sessions = static.TERMS[state][-1]['sessions']
            bills = bills.filter(legislative_session__identifier__in=latest_sessions)
        elif search_window.startswith('session:'):
            bills = bills.filter(legislative_session__identifier=search_window.split('session:')[1])
        elif search_window != 'all':
            raise ValueError('invalid search_window. valid choices are "term", "session", "all"')

    # first, last, created
    if sort == 'created_at':
        bills = bills.order_by('-created_at')
    elif sort == 'updated_at':
        bills = bills.order_by('-updated_at')
    else:
        bills = bills.annotate(latest_action=Max('actions__date')).order_by('-latest_action')

    # pagination
    page = request.GET.get('page')
    per_page = request.GET.get('per_page')
    if page and not per_page:
        per_page = 50
    if per_page and not page:
        page = 1

    if page:
        page = int(page)
        per_page = int(per_page)
        start = per_page * (page - 1)
        end = start + per_page
        bills = bills[start:end]
    else:
        # limit response size
        if len(bills) > 1000:
            return JsonResponse("Bad Request: request too large, try narrowing your search by "
                                "adding more filters.", status=400, safe=False)

    return JsonResponse([utils.convert_bill(b) for b in bills], safe=False)
