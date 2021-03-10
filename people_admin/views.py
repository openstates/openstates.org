from django.shortcuts import render, get_object_or_404
from openstates.data.models import LegislativeSession, Person
from utils.common import abbr_to_jid, sessions_with_bills, states
from people_admin.models import UnmatchedName

# from django.views.decorators.http import require_http_methods


def people_list(request):
    state_people_data = {}

    for state in states:
        state_people_data[state.abbr.lower()] = {
            "state": state.name,
        }

    return render(
        request,
        "people_admin/people_listing.html",
        {"state_people_data": state_people_data},
    )


def people_matcher(request, state, session=None):
    jid = abbr_to_jid(state)
    all_sessions = sessions_with_bills(jid)
    if all_sessions:
        session = all_sessions[0]
    else:
        session = get_object_or_404(
            LegislativeSession, identifier=session, jurisdiction_id=jid
        )

    unmatched = UnmatchedName.objects.filter(session_id=session)
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


# pseudo-code for apply_match view:

# @require_http_methods(["POST"])
# def apply_match(request):
#     button = request.POST["submit"]
#     match_id = request.POST["match_id"]
#     unmatched_id = request.POST["unmatched_id"]
#
#     unmatched_name = get_object_or_404(UnmatchedName, pk=unmatched_id)
#
#     if button == "match":
#         unmatched_name.person_id = match_id
#         unmatched_name.status = NameStatues.MATCHED_PERSON
#     elif button == "source_error":
#         unmatched_name.status = NameStatus.SOURCE_ERROR
#     elif button == "ignore":
#         unmatched_name.status = NameStatus.IGNORED
#     else:
#         unmatched_name.status = NameStatus.UNMATCHED
#
#     unmatched_name.save()
#
#     return JSONResponse({"status": "success"})
