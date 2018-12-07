from django.db.models import Max, Min, Func
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from opencivicdata.legislative.models import Bill, LegislativeSession
from utils.common import abbr_to_jid
from utils.orgs import get_chambers_from_abbr
from utils.bills import fix_bill_id


class Unnest(Func):
    function = 'UNNEST'


def bills(request, state):
    """
        form values:
            query
            chamber: lower|upper
            session
            bill-status: passed-lower-chamber|passed-upper-chamber|signed-into-law
            sponsor:
            type:
            subjects:
    """
    bills = Bill.objects.all().annotate(
        first_action_date=Min('actions__date'),
    )
    jid = abbr_to_jid(state)
    bills = bills.filter(legislative_session__jurisdiction_id=jid)

    # filter options
    chambers = get_chambers_from_abbr(state)
    chambers = {c.classification: c.name for c in chambers}
    sessions = LegislativeSession.objects.filter(jurisdiction_id=jid).order_by('-start_date')
    sponsors = []    # TODO
    types = ['bill', 'resolution']  # TODO
    subjects = sorted(bills.annotate(sub=Unnest('subject', distinct=True)).values_list('sub', flat=True).distinct())


    # query parameter filtering
    query = request.GET.get('query')
    chamber = request.GET.get('chamber')
    session = request.GET.get('session')
    if query:
        bills = bills.filter(title__icontains=query)
    if chamber:
        bills = bills.filter(from_organization__classification=chamber)
    if session:
        bills = bills.filter(legislative_session__identifier=session)

    # pagination
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(bills, 20)
    bills = paginator.page(page_num)

    # augment
    for bill in bills.object_list:
        bill.latest_action = bill.actions.order_by('date').last()
        print(type(bill.first_action_date))

    return render(
        request,
        'public/views/bills.html',
        {
            'state': state,
            'bills': bills,
            'chambers': chambers,
            'sessions': sessions,
            'sponsors': sponsors,
            'types': types,
            'subjects': subjects,
        }
    )


def bill(request, state, session, bill_id):
    jid = abbr_to_jid(state)
    identifier = fix_bill_id(bill_id)
    bill = get_object_or_404(Bill,
                             legislative_session__jurisdiction_id=jid,
                             legislative_session__identifier=session,
                             identifier=identifier)

    return render(
        request,
        'public/views/bill.html',
        {
            'state': state,
            'bill': bill
        }
    )
