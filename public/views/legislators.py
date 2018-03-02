from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from opencivicdata.core.models import Person
import us

from .mock import LEGISLATOR_VOTES
from ..utils import get_legislative_post, get_legislature_from_state_abbr


def legislators(request, state):
    legislature = get_legislature_from_state_abbr(state)
    chambers = legislature.children.filter(
        Q(classification='lower') |
        Q(classification='upper')
    )

    legislators = (
        {
            'headshot_url': '',
            'id': p.id,
            'name': p.name,
            'party': p.memberships.get(organization__classification='party').organization.name,
            'district': get_legislative_post(p).label,
            'chamber': get_legislative_post(p).organization.classification
        }
        for p
        in Person.objects.filter(
            Q(memberships__organization=legislature) |
            Q(memberships__organization__in=chambers)
        )
    )

    return render(
        request,
        'public/views/legislators.html',
        {
            'state': state,
            'state_name': us.states.lookup(state).name,
            'legislators': legislators
        }
    )


def legislator(request, state, legislator_id):
    person = get_object_or_404(Person, pk=legislator_id)
    # TO DO
    headshot_url = ''
    party = person.memberships.get(organization__classification='party').organization.name
    legislative_post = person.memberships.get(
        Q(organization__classification='legislature') |
        Q(organization__classification='lower') |
        Q(organization__classification='upper')
    ).post

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
        person.billsponsorship_set.all().order_by('bill__created_at', 'bill_id')[:4]
    ]

    # TO DO
    votes = LEGISLATOR_VOTES

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
