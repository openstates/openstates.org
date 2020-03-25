from collections import defaultdict
from .models import Bundle
from django.shortcuts import render_to_response


def bundle_view(request, slug):
    bundle = Bundle.objects.get(slug=slug)
    bills_by_state = defaultdict(list)
    total_bills = 0

    for bill in bundle.bills.all().select_related("legislative_session__jurisdiction"):
        bills_by_state[bill.legislative_session.jurisdiction.name].append(bill)
        total_bills += 1

    bills_by_state = {
        state: sorted(bills, key=lambda b: b.identifier)
        for state, bills in sorted(bills_by_state.items())
    }

    return render_to_response(
        "bundles/bundle.html",
        {
            "bundle": bundle,
            "bills_by_state": bills_by_state,
            "total_bills": total_bills,
        },
    )
