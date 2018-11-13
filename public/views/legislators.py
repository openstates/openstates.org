from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from opencivicdata.core.models import Person
from graphapi.schema import schema
from utils.people import get_current_role

from ..utils import (
    get_chambers_from_state_abbr,
    get_legislative_post
)


def _people_from_lat_lon(lat, lon):
    PERSON_GEO_QUERY = """{
      people(latitude: %s, longitude: %s, first: 10) {
        edges {
          node {
            name
            currentMemberships(classification: ["upper", "lower", "legislature", "party"]) {
              post {
                label
                division { id }
              }
              organization {
                classification
                name
              }
            }
          }
        }
      }
    }"""
    resp = schema.execute(PERSON_GEO_QUERY % (lat, lon))

    nodes = [node['node'] for node in resp.data['people']['edges']]
    people = []
    for node in nodes:
        person = {
            'name': node['name'],
        }
        for m in node['currentMemberships']:
            if m['organization']['classification'] == 'party':
                person['party'] = m['organization']['name']
            else:
                person['chamber'] = m['organization']['classification']
                person['district'] = m['post']['label']
                person['division_id'] = m['post']['division']['id']
        people.append(person)

    return people


def _template_person(person):
    cr = get_current_role(person)
    try:
        district = int(cr['district'])
    except ValueError:
        district = cr['district']

    obj = {
        'id': person.id,
        'name': person.name,
        'image': person.image,
        'party': cr['party'],
        'district': district,
        'chamber': cr['chamber'],
        }
    return obj


def find_your_legislator(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if lat and lon:
        # got a passed lat/lon. Let's build off it.
        people = _people_from_lat_lon(lat, lon)
        return JsonResponse({'legislators': people})

    context = {
        'disable_state_nav': True,
    }
    return render(request, 'public/views/find_your_legislator.html', context)


def legislators(request, state):
    chambers = get_chambers_from_state_abbr(state)

    legislators = [
        _template_person(p)
        for p in Person.objects.filter(memberships__organization__in=chambers)
    ]

    chambers = {c.classification: c.name for c in chambers}

    return render(
        request,
        'public/views/legislators.html',
        {
            'state': state,
            'chambers': chambers,
            'legislators': legislators,
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
