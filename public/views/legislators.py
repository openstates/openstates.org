from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from opencivicdata.core.models import Person
from graphapi.schema import schema
from utils.common import decode_uuid, pretty_url
from utils.people import get_current_role
from utils.orgs import get_chambers_from_abbr


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
        'pretty_url': pretty_url(person),
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
    chambers = get_chambers_from_abbr(state)

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


def person(request, person_id):
    SPONSORED_BILLS_TO_SHOW = 4
    RECENT_VOTES_TO_SHOW = 3

    ocd_person_id = decode_uuid(person_id)
    person = get_object_or_404(Person, pk=ocd_person_id)

    cur_role = get_current_role(person)

    person.party = cur_role['party']
    person.role = cur_role['role']
    person.district = cur_role['district']
    state = cur_role['state']

    person.committee_memberships = person.memberships.filter(
        organization__classification='committee').all()

    person.all_contact_details = person.contact_details.order_by('note')

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
        }
    )
