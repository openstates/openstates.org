from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from opencivicdata.core.models import Person

from .mock import LEGISLATOR_VOTES


def legislators(request, state):
    return render(
        request,
        'public/views/legislators.html',
        {
            'state': state
        }
    )


def legislator(request, state, legislator_id):
    person = get_object_or_404(Person, pk=legislator_id)
    # TO DO
    headshot_url = ''
    party = person.memberships.get(organization__classification='party').organization.name
    legislative_membership = person.memberships.get(
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

    legislature = legislative_membership.organization.parent or legislative_membership.organization
    jurisdiction = legislature.jurisdiction
    sources = {
        'legislature_name': legislature.name,
        'jurisdiction_url': jurisdiction.url,
        'urls': person.sources.all()
    }

    return render(
        request,
        'public/views/legislator.html',
        {
            'state': state,

            'name': person.name,
            'headshot_url': headshot_url,
            'party': party,
            'title': legislative_membership.role,
            'district': legislative_membership.label,
            'division_id': legislative_membership.division_id,

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
