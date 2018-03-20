from django.db.models import Min
from django.shortcuts import get_object_or_404, render
from opencivicdata.legislative.models import Bill

from ..utils import get_chambers_from_state_abbr


def bills(request, state):
    chambers = get_chambers_from_state_abbr(state)

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


def bill(request, state, bill_id):
    bill = get_object_or_404(Bill, pk=bill_id)

    return render(
        request,
        'public/views/bill.html',
        {
            'state': state,
            'bill': bill
        }
    )
