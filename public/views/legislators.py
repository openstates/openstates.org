from django.db.models import F
from django.db.models.functions import Substr
from django.shortcuts import get_object_or_404, render
from opencivicdata.core.models import Person

from ..utils import (
    get_chambers_from_state_abbr,
    get_legislative_post
)


def legislators(request, state):
    chambers = get_chambers_from_state_abbr(state)

    legislators = (
        {
            'headshot_url': '',
            'id': p.id,
            'name': p.name,
            'party': p.memberships.filter(
                organization__classification='party').last().organization.name,
            'district': get_legislative_post(p).label,
            'chamber': get_legislative_post(p).organization.classification
        }
        for p
        in Person.objects.filter(memberships__organization__in=chambers)
    )

    return render(
        request,
        'public/views/legislators.html',
        {
            'state': state,
            'legislators': legislators
        }
    )


def legislator(request, state, legislator_id):
    SPONSORED_BILLS_TO_SHOW = 4
    RECENT_VOTES_TO_SHOW = 3

    person = get_object_or_404(Person, pk=legislator_id)
    # TO DO
    headshot_url = ''
    party = person.memberships.get(organization__classification='party').organization.name
    legislative_post = get_legislative_post(person)

    # These contact information values may not exist, so allow database fetch to find nothing
    email = getattr(person.contact_details.filter(type='email').first(), 'value', None)
    capitol_address = getattr(person.contact_details.filter(note='Capitol Office').first(),
                              'value', None)
    capitol_phone = getattr(person.contact_details.filter(note='Capitol Office Phone').first(),
                            'value', None)
    district_address = getattr(person.contact_details.filter(note='District Office').first(),
                               'value', None)
    district_phone = getattr(person.contact_details.filter(note='District Office Phone').first(),
                             'value', None)

    committee_memberships = person.memberships.filter(
        organization__classification='committee').all()

    sponsored_bills = [
        sponsorship.bill for sponsorship in
        person.billsponsorship_set.all().order_by(
            'bill__created_at', 'bill_id'
        )[:SPONSORED_BILLS_TO_SHOW]
    ]

    votes = person.votes.order_by('-vote_event__start_date')[:RECENT_VOTES_TO_SHOW].annotate(
        start_date=Substr(F('vote_event__start_date'), 1, 10),
        bill_identifier=F('vote_event__bill__identifier'),
        motion_text=F('vote_event__motion_text'),
        legislator_vote=F('option'),
        result=F('vote_event__result')
    ).values()

    sources = person.sources.all()

    return render(
        request,
        'public/views/legislator.html',
        {
            'state': state,

            'name': person.name,
            'headshot_url': headshot_url,
            'party': party,
            'title': legislative_post.role,
            'district': legislative_post.label,
            'division_id': legislative_post.division_id,

            'email': email,
            'capitol_address': capitol_address,
            'capitol_phone': capitol_phone,
            'district_address': district_address,
            'district_phone': district_phone,

            'committees': committee_memberships,

            'sponsored_bills': sponsored_bills,

            'votes': votes,

            'sources': sources
        }
    )
