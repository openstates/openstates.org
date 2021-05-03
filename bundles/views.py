import csv
from collections import defaultdict
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import F
from utils.common import pretty_url
from .models import Bundle


def bundle_view(request, slug):
    bundle = Bundle.objects.get(slug=slug)
    bills_by_state = defaultdict(list)
    total_bills = 0

    for bill in bundle.bills.all().select_related(
        "legislative_session__jurisdiction",
    ):
        bills_by_state[bill.legislative_session.jurisdiction.name].append(bill)
        total_bills += 1

    bills_by_state = {
        state: sorted(bills, key=lambda b: b.identifier)
        for state, bills in sorted(bills_by_state.items())
    }

    return render(
        request,
        "bundles/bundle.html",
        {
            "bundle": bundle,
            "bills_by_state": bills_by_state,
            "total_bills": total_bills,
        },
    )


def csv_view(request, slug):
    bundle = Bundle.objects.get(slug=slug)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{slug}.csv"'

    writer = csv.DictWriter(
        response,
        fieldnames=[
            "state",
            "session",
            "identifier",
            "title",
            "introduced",
            "latest_action_description",
            "latest_action_date",
            "openstates_url",
        ],
    )
    writer.writeheader()

    for bill in (
        bundle.bills.all()
        .select_related(
            "legislative_session__jurisdiction",
        )
        .order_by(F("first_action_date").desc(nulls_last=True))
    ):
        writer.writerow(
            {
                "state": bill.legislative_session.jurisdiction.name,
                "session": bill.legislative_session.identifier,
                "identifier": bill.identifier,
                "title": bill.title,
                "introduced": bill.first_action_date,
                "latest_action_date": bill.latest_action_date,
                "latest_action_description": bill.latest_action_description,
                "openstates_url": "https://openstates.org/" + pretty_url(bill),
            }
        )
    return response
