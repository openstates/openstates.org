from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from graphapi.schema import schema
from openstates.data.models import Person, Bill
from utils.common import decode_uuid, jid_to_abbr, pretty_url
from utils.orgs import get_chambers_from_abbr
from utils.people import person_as_dict


def _people_from_lat_lon(lat, lon):
    PERSON_GEO_QUERY = """{
      people(latitude: %s, longitude: %s, first: 10) {
        edges {
          node {
            id
            image
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

    nodes = [node["node"] for node in resp.data["people"]["edges"]]
    people = []
    for node in nodes:
        person = {
            "name": node["name"],
            "id": node["id"],
            "image": node["image"],
            "pretty_url": pretty_url(node),
        }
        for m in node["currentMemberships"]:
            if m["organization"]["classification"] == "party":
                person["party"] = m["organization"]["name"]
            else:
                person["chamber"] = m["organization"]["classification"]
                person["district"] = m["post"]["label"]
                person["division_id"] = m["post"]["division"]["id"]
        people.append(person)

    return people


def find_your_legislator(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    json = request.GET.get("json")

    if json and lat and lon:
        # got a passed lat/lon. Let's build off it.
        people = _people_from_lat_lon(lat, lon)
        return JsonResponse({"legislators": people})

    return render(request, "public/views/find_your_legislator.html", {})


def legislators(request, state):
    chambers = get_chambers_from_abbr(state)

    legislators = [
        person_as_dict(p)
        for p in Person.objects.current_legislators_with_roles(chambers)
    ]

    chambers = {c.classification: c.name for c in chambers}

    return render(
        request,
        "public/views/legislators.html",
        {
            "state": state,
            "chambers": chambers,
            "legislators": legislators,
            "state_nav": "legislators",
        },
    )


def person(request, person_id):
    SPONSORED_BILLS_TO_SHOW = 4
    RECENT_VOTES_TO_SHOW = 3

    try:
        ocd_person_id = decode_uuid(person_id)
    except ValueError:
        ocd_person_id = (
            person_id  # will be invalid and raise 404, but useful in logging later
        )
    person = get_object_or_404(
        Person.objects.prefetch_related("memberships__organization"), pk=ocd_person_id,
    )

    # to display district in front of district name, or not?
    district_maybe = ""

    # canonicalize the URL
    canonical_url = pretty_url(person)
    if request.path != canonical_url:
        return redirect(canonical_url, permanent=True)

    if not person.current_role:
        #  this breaks if they held office in two states, but we don't really worry about that
        for m in person.memberships.all():
            if m.organization.classification in ("upper", "lower", "legislature"):
                state = jid_to_abbr(m.organization.jurisdiction_id)
        retired = True
    else:
        state = jid_to_abbr(person.current_jurisdiction_id)
        retired = False
        # does it start with a number?
        if str(person.current_role["district"])[0] in "0123456789":
            district_maybe = "District"
    person.all_contact_details = person.contact_details.order_by("note")

    person.sponsored_bills = list(
        Bill.objects.all()
        .select_related("legislative_session", "legislative_session__jurisdiction",)
        .filter(sponsorships__person=person)
        .order_by("-created_at", "id")[:SPONSORED_BILLS_TO_SHOW]
    )

    person.committee_memberships = person.memberships.filter(
        organization__classification="committee"
    ).all()

    votes = person.votes.all().select_related("vote_event", "vote_event__bill")[
        :RECENT_VOTES_TO_SHOW
    ]
    person.vote_events = []
    for vote in votes:
        vote_event = vote.vote_event
        vote_event.legislator_vote = vote
        person.vote_events.append(vote_event)

    return render(
        request,
        "public/views/legislator.html",
        {
            "state": state,
            "person": person,
            "state_nav": "legislators",
            "retired": retired,
            "district_maybe": district_maybe,
        },
    )
