from collections import Counter

from django.shortcuts import render
from opencivicdata.core.models import Person, Organization
from opencivicdata.legislative.models import Bill, VoteEvent

from ..utils import (
    get_chambers_from_state_abbr
)


def styleguide(request):
    return render(request, 'public/views/styleguide.html')


def home(request):
    return render(request, 'public/views/home.html')


def state(request, state):
    chambers = get_chambers_from_state_abbr(state)
    legislature = chambers[0].parent if chambers[0].parent else chambers[0]

    for chamber in chambers:
        # For the party-count section
        chamber.seats = sum([post.maximum_memberships for post in chamber.posts.all()])
        legislators = chamber.get_current_members()
        parties = [
            legislator.memberships.filter(organization__classification='party').last().organization.name
            for legislator in legislators
        ]
        chamber.parties = dict(Counter(parties))
        chamber.parties['Vacancies'] = chamber.seats - len(legislators)

        # For the committee-count block
        chamber.committee_count = chamber.children.filter(classification='committee').count() or 0
    # This will re-assign for unicameral legislatures, but that's okay
    legislature.committee_count = legislature.children.filter(classification='committee').count()

    return render(
        request,
        'public/views/state.html',
        {
            'state': state,

            'legislature': legislature,
            'chambers': chambers,
        }
    )
