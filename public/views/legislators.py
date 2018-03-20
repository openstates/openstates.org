from django.shortcuts import get_object_or_404, render
from opencivicdata.core.models import Person

from ..utils import (
    get_chambers_from_state_abbr,
    get_legislative_post
)


def legislators(request, state):
    chambers = get_chambers_from_state_abbr(state)

    legislators = [
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
    ]

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
    person.headshot_url = ''

    person.party = person.memberships.get(organization__classification='party').organization.name
    person.legislative_post = get_legislative_post(person)
    person.committee_memberships = person.memberships.filter(
        organization__classification='committee').all()

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

    person.sponsored_bills = [
        sponsorship.bill for sponsorship in
        person.billsponsorship_set.all().order_by(
            'bill__created_at', 'bill_id'
        )[:SPONSORED_BILLS_TO_SHOW]
    ]

    votes = person.votes.all()[:RECENT_VOTES_TO_SHOW]
    person.vote_events = []
    for vote in votes:
        vote_event = vote.vote_event
        vote_event.legislator_vote = vote
        person.vote_events.append(vote_event)

    return render(
        request,
        'public/views/legislator.html',
        {
            'state': state,

            'person': person,

            'email': email,
            'capitol_address': capitol_address,
            'capitol_phone': capitol_phone,
            'district_address': district_address,
            'district_phone': district_phone
        }
    )
