from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from openstates.data.models import LegislativeSession, Person
from utils.common import abbr_to_jid, sessions_with_bills, states
from people_admin.models import UnmatchedName, NameStatus

from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
import json


def person_data(person):
    """ similar to utils.people.person_as_dict but customized for editable fields """
    return {
        "id": person.id,
        "name": person.name,
        "title": person.current_role["title"],
        "district": person.current_role["district"],
        "party": person.primary_party,
        "image": person.image,
    }


@user_passes_test(lambda u: u.is_staff)
def jurisdiction_list(request):
    state_people_data = {}

    unmatched_by_state = dict(
        UnmatchedName.objects.filter(status="U")
        .values_list("session__jurisdiction__name")
        .annotate(number=Count("id"))
    )

    for state in states:
        state_people_data[state.abbr.lower()] = {
            "state": state.name,
            "unmatched": unmatched_by_state.get(state.name, 0),
        }

    return render(
        request,
        "people_admin/jurisdiction_list.html",
        {"state_people_data": state_people_data},
    )


@never_cache
@user_passes_test(lambda u: u.is_staff)
def people_list(request, state):
    jid = abbr_to_jid(state)
    current_people = [
        person_data(p)
        for p in Person.objects.filter(
            current_jurisdiction_id=jid, current_role__isnull=False
        ).order_by("family_name", "name")
    ]

    context = {
        "current_people": current_people,
    }

    return render(request, "people_admin/person_list.html", {"context": context})


@never_cache
@user_passes_test(lambda u: u.is_staff)
def people_matcher(request, state, session=None):
    jid = abbr_to_jid(state)
    all_sessions = sessions_with_bills(jid)
    if all_sessions:
        session = all_sessions[0]
    else:
        session = get_object_or_404(
            LegislativeSession, identifier=session, jurisdiction_id=jid
        )

    unmatched = UnmatchedName.objects.filter(session_id=session, status="U").order_by(
        "-sponsorships_count"
    )
    state_sponsors = Person.objects.filter(current_jurisdiction_id=jid)
    unmatched_total = unmatched.count()

    context = {
        "state": state,
        "session": session,
        "all_sessions": all_sessions,
        "unmatched": unmatched,
        "state_sponsors": state_sponsors,
        "unmatched_total": unmatched_total,
    }

    return render(request, "people_admin/people_matcher.html", context)


@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["POST"])
def apply_match(request):
    form_data = json.load(request)["match_data"]
    button = form_data["button"]
    match_id = form_data["matchedId"]
    unmatched_id = form_data["unmatchedId"]

    unmatched_name = get_object_or_404(UnmatchedName, pk=unmatched_id)

    if button == "Match":
        unmatched_name.matched_person_id = match_id
        unmatched_name.status = NameStatus.MATCHED_PERSON
    elif button == "Source Error":
        unmatched_name.status = NameStatus.SOURCE_ERROR
    elif button == "Ignore":
        unmatched_name.status = NameStatus.IGNORED
    else:
        unmatched_name.status = NameStatus.UNMATCHED

    unmatched_name.save()

    return JsonResponse({"status": "success"})
