from collections import Counter

from django.db.models import Min, Max
from django.shortcuts import render
from opencivicdata.legislative.models import Bill
from utils.orgs import get_chambers_from_abbr


def styleguide(request):
    return render(request, 'public/views/styleguide.html')


def home(request):
    return render(request, 'public/views/home.html')


def state(request, state):
    RECENTLY_INTRODUCED_BILLS_TO_SHOW = 4
    RECENTLY_PASSED_BILLS_TO_SHOW = 4

    chambers = get_chambers_from_abbr(state)
    legislature = chambers[0].parent if chambers[0].parent else chambers[0]

    for chamber in chambers:
        # For the party-count section
        chamber.seats = sum([post.maximum_memberships for post in chamber.posts.all()])
        legislators = chamber.get_current_members()
        parties = [
            # After resolving multiple-party individuals, we'll have
            # a simpler way to return party
            legislator.memberships.filter(
                organization__classification='party').last().organization.name
            for legislator in legislators
        ]
        chamber.parties = dict(Counter(parties))
        chamber.parties['Vacancies'] = chamber.seats - len(legislators)

        # For the committee-count block
        chamber.committee_count = chamber.children.filter(classification='committee').count() or 0
    # This will re-assign for unicameral legislatures, but that's okay
    legislature.committee_count = legislature.children.filter(classification='committee').count()

    bills = Bill.objects.filter(from_organization__in=chambers)

    recently_introduced_bills = bills.filter(
        actions__isnull=False
    ).annotate(
        introduced_date=Min('actions__date'),
    ).order_by('-introduced_date')[:RECENTLY_INTRODUCED_BILLS_TO_SHOW]

    recently_passed_bills = bills.filter(
        actions__classification__contains=['passage']
    ).annotate(
        passed_date=Max('actions__date')
    ).order_by('-passed_date')[:RECENTLY_PASSED_BILLS_TO_SHOW]

    return render(
        request,
        'public/views/state.html',
        {
            'state': state,

            'legislature': legislature,
            'chambers': chambers,

            'recently_introduced_bills': recently_introduced_bills,
            'recently_passed_bills': recently_passed_bills
        }
    )
