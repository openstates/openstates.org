from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from graphapi.schema import schema
from utils.common import decode_uuid
from utils.orgs import get_chambers_from_abbr
from ..models import PersonProxy


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


def find_your_legislator(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if lat and lon:
        # got a passed lat/lon. Let's build off it.
        people = _people_from_lat_lon(lat, lon)
        return JsonResponse({'legislators': people})

    context = {
        'state_nav': 'disabled',
    }
    return render(request, 'public/views/find_your_legislator.html', context)


def legislators(request, state):
    chambers = get_chambers_from_abbr(state)

    legislators = [
        p.as_dict()
        for p in PersonProxy.objects.filter(memberships__organization__in=chambers).prefetch_related("memberships", "memberships__organization", "memberships__post")
    ]

    chambers = {c.classification: c.name for c in chambers}

    return render(
        request,
        'public/views/legislators.html',
        {
            'state': state,
            'chambers': chambers,
            'legislators': legislators,
            'state_nav': 'legislators',
        }
    )


def person(request, person_id):
    SPONSORED_BILLS_TO_SHOW = 4
    RECENT_VOTES_TO_SHOW = 3

    ocd_person_id = decode_uuid(person_id)
    person = get_object_or_404(PersonProxy.objects.prefetch_related("memberships__organization"), pk=ocd_person_id)

    state = person.current_role['state']
    person.all_contact_details = person.contact_details.order_by('note')

    person.sponsored_bills = [
        sponsorship.bill for sponsorship in
        person.billsponsorship_set.all().select_related("bill").order_by(
            'bill__created_at', 'bill_id'
        )[:SPONSORED_BILLS_TO_SHOW]
    ]

    votes = person.votes.all().select_related("vote_event", "vote_event__bill")[:RECENT_VOTES_TO_SHOW]
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
            'state_nav': 'legislators',
        }
    )
