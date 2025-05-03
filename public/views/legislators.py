from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from graphapi.schema import schema
from openstates.data.models import Person, Bill
from utils.common import decode_uuid, jid_to_abbr, pretty_url
from utils.orgs import get_chambers_from_abbr
from utils.people import person_as_dict


def _people_from_lat_lon(lat, lon):
    PERSON_GEO_QUERY = """{
      people(latitude: %s, longitude: %s, first: 15) {
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
                jurisdictionId
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
                person["jurisdiction_id"] = m["organization"]["jurisdictionId"]
                person["level"] = (
                    "federal"
                    if m["organization"]["jurisdictionId"]
                    == "ocd-jurisdiction/country:us/government"
                    else "state"
                )
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
    try:
        ocd_person_id = decode_uuid(person_id)
    except ValueError:
        ocd_person_id = (
            person_id  # will be invalid and raise 404, but useful in logging later
        )
    redirect_person_id = ocd_person_id.replace("ocd-person/", "")
    return redirect(f"https://pluralpolicy.com/app/person/{redirect_person_id}/", permanent=True)
