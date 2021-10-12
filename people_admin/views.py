import json
import us
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from openstates.data.models import LegislativeSession, Person
from utils.common import abbr_to_jid, sessions_with_bills, states
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .unmatched import unmatched_to_deltas
from people_admin.models import (
    UnmatchedName,
    NameStatus,
    DeltaSet,
    PersonDelta,
    PersonRetirement,
    NewPerson,
)
from people_admin.git import delta_set_to_pr


MATCHER_PERM = "people_admin.can_match_names"
EDIT_PERM = "people_admin.can_edit"
RETIRE_PERM = "people_admin.can_retire"


def person_data(person):
    """similar to utils.people.person_as_dict but customized for editable fields"""
    extras = {}
    identifier_types = ("twitter", "facebook", "instagram", "youtube")
    for identifier in person.identifiers.all():
        for itype in identifier_types:
            if identifier.scheme == itype:
                extras[itype] = identifier.identifier
    for off in person.offices.all():
        if off.fax:
            extras[off.classification + "_fax"] = off.fax
        if off.voice:
            extras[off.classification + "_voice"] = off.voice
        if off.address:
            extras[off.classification + "_address"] = off.address
    return {
        "id": person.id,
        "name": person.name,
        "title": person.current_role["title"],
        "district": person.current_role["district"],
        "party": person.primary_party,
        "image": person.image,
        "email": person.email,
        **extras,
    }


@user_passes_test(lambda u: u.has_perm(MATCHER_PERM) or u.has_perm(EDIT_PERM))
def jurisdiction_list(request):
    state_people_data = {}

    unmatched_by_state = dict(
        UnmatchedName.objects.filter(status="U")
        .values_list("session__jurisdiction__name")
        .annotate(number=Count("id"))
    )

    for state in states + [us.unitedstatesofamerica]:
        jid = abbr_to_jid(state.abbr)
        current_people = [
            person_data(p)
            for p in Person.objects.filter(
                current_jurisdiction_id=jid, current_role__isnull=False
            ).prefetch_related("offices")
        ]
        photoless = 0
        phoneless = 0
        addressless = 0
        for person in current_people:
            if "image" not in person or person["image"] == "":
                photoless += 1
            elif "capitol_voice" not in person and "district_voice" not in person:
                phoneless += 1
            elif "capitol_address" not in person and "district_address" not in person:
                addressless += 1

        jurisdiction = "United States" if state.abbr == "US" else state.name

        state_people_data[state.abbr.lower()] = {
            "state": jurisdiction,
            "unmatched": unmatched_by_state.get(state.name, 0),
            "missing_photo": photoless,
            "missing_phone": phoneless,
            "missing_address": addressless,
        }

    return render(
        request,
        "people_admin/jurisdiction_list.html",
        {"state_people_data": state_people_data},
    )


@never_cache
@user_passes_test(lambda u: u.has_perm(EDIT_PERM))
def people_list(request, state):
    jid = abbr_to_jid(state)
    current_people = [
        person_data(p)
        for p in Person.objects.filter(
            current_jurisdiction_id=jid, current_role__isnull=False
        )
        .order_by("family_name", "name")
        .prefetch_related("identifiers", "offices")
    ]

    context = {
        "current_people": current_people,
    }

    return render(request, "people_admin/person_list.html", {"context": context})


@never_cache
@user_passes_test(lambda u: u.has_perm(MATCHER_PERM))
def people_matcher(request, state, session=None):
    jid = abbr_to_jid(state)
    all_sessions = sessions_with_bills(jid)

    if session:
        session = get_object_or_404(
            LegislativeSession, identifier=session, jurisdiction_id=jid
        )
        unmatched = UnmatchedName.objects.filter(
            session_id=session, status="U"
        ).order_by("-sponsorships_count")
    else:
        unmatched = UnmatchedName.objects.filter(
            session__jurisdiction__id=jid, status="U"
        ).order_by("-sponsorships_count")
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


@user_passes_test(lambda u: u.has_perm(MATCHER_PERM))
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


@user_passes_test(lambda u: u.has_perm(RETIRE_PERM))
@require_http_methods(["POST"])
def apply_retirement(request):
    retirement = json.load(request)
    name = retirement["name"]
    delta = DeltaSet.objects.create(
        name=f"retire {name}",
        created_by=request.user,
    )
    PersonRetirement.objects.create(
        delta_set=delta,
        person_id=retirement["id"],
        date=retirement["retirementDate"],
        reason=retirement["reason"] or "",
        is_dead=retirement["isDead"],
        is_vacant=retirement["vacantSeat"],
    )
    return JsonResponse({"status": "success"})


@user_passes_test(lambda u: u.has_perm(EDIT_PERM))
def new_legislator(request, state):
    context = {
        "state": state,
    }

    return render(request, "people_admin/new_person.html", {"context": context})


@user_passes_test(lambda u: u.has_perm(EDIT_PERM))
@require_http_methods(["POST"])
def apply_new_legislator(request):
    addition = json.load(request)
    name = addition[person_data]["name"]
    delta = DeltaSet.objects.create(
        name=f"add {name}",
        created_by=request.user,
    )
    NewPerson.objects.create(
        name=name,
        delta_set=delta,
        state=addition["state"],
        district=addition["district"],
        chamber=addition["chamber"],
    )
    return JsonResponse({"status": "success"})


@user_passes_test(lambda u: u.has_perm(EDIT_PERM))
@require_http_methods(["POST"])
def apply_bulk_edits(request):
    edits = json.load(request)

    delta = DeltaSet.objects.create(
        name=f"edit by {request.user}",
        created_by=request.user,
    )

    for person in edits:
        updates = []
        for key in person:
            if key != "id":
                change = {"action": "set", "key": key, "param": person[key]}
                updates.append(change)
        PersonDelta.objects.create(
            delta_set=delta,
            person_id=person["id"],
            data_changes=updates,
        )
    return JsonResponse({"status": "success"})


@never_cache
@user_passes_test(lambda u: u.has_perm(EDIT_PERM))
def create_delta_sets(request, state):
    matches = unmatched_to_deltas(state)
    name = f"{state.upper()} legislator matching"
    delta = DeltaSet.objects.get(name=name, pr_status="N")
    people_deltas = PersonDelta.objects.filter(delta_set_id=delta).order_by("person_id")
    context = {
        "people": people_deltas,
        "matches": matches,
    }

    return render(request, "people_admin/deltasets.html", context)


@never_cache
@user_passes_test(lambda u: u.has_perm(EDIT_PERM))
@require_http_methods(["POST"])
def create_pr(request):
    delta = json.load(request)["delta"]
    ds = DeltaSet.objects.get(id=delta, pr_status="N")
    print(f"creating {ds.id} | {ds.name} | {ds.created_by}")
    ds.pr_url = delta_set_to_pr(ds)
    ds.pr_status = "C"
    ds.save()
    return JsonResponse({"status": request})
