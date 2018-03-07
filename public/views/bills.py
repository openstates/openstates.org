from django.db.models import Min
from django.shortcuts import render
from opencivicdata.legislative.models import Bill

from ..utils import get_chambers_from_state_abbr


def bills(request, state):
    chambers = get_chambers_from_state_abbr(state)
    # import pdb; pdb.set_trace()
    bills = [
        # Doing this in a list comprehension instead of an `annotate`
        # because syntax is way simpler in this construction
        {
            'identifier': bill.identifier,
            'legislative_session': bill.legislative_session.name,
            'title': bill.title,
            'introduced': bill.actions.aggregate(Min('date')).get('date__min'),
            'latest_action': bill.actions.order_by('date').last()
        }
        for bill
        in Bill.objects.filter(from_organization__in=chambers)[:8]
    ]

    return render(
        request,
        'public/views/bills.html',
        {
            'state': state,
            'bills': bills
        }
    )


def bill(request, state):
    return render(
        request,
        'public/views/bill.html',
        {
            'state': state
        }
    )
