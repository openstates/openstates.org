from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from opencivicdata.core.models import Person


def base(request):
    return render(request, 'public/components/base.html')


def legislators(request):
    return render(request, 'public/views/legislators.html')


def legislator(request, legislator_id):
    person = get_object_or_404(Person, pk=legislator_id)
    party = person.memberships.get(organization__classification='party').organization.name
    legislative_membership = person.memberships.get(
        Q(organization__classification='legislature') |
        Q(organization__classification='lower') |
        Q(organization__classification='upper')
    ).post

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
    votes = []

    sources = [source.url for source in person.sources.all()]

    return render(
        request,
        'public/views/legislator.html',
        {
            'name': person.name,
            'party': party,
            'title': legislative_membership.role,
            'district': legislative_membership.label,

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
