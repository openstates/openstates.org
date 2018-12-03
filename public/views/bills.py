from django.db.models import Min
from django.shortcuts import get_object_or_404, render
from opencivicdata.legislative.models import Bill
from utils.common import abbr_to_jid
from utils.orgs import get_chambers_from_abbr
from utils.bills import fix_bill_id


def bills(request, state):
    chambers = get_chambers_from_abbr(state)

    bills = Bill.objects.filter(from_organization__in=chambers)[:8]
    for bill in bills:
        bill.introduced = bill.actions.aggregate(Min('date')).get('date__min')
        bill.latest_action = bill.actions.order_by('date').last()

    return render(
        request,
        'public/views/bills.html',
        {
            'state': state,
            'bills': bills
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
