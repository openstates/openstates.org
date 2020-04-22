from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F
from openstates.data.models import Organization, Person
from utils.common import decode_uuid, pretty_url
from utils.orgs import get_chambers_from_abbr, org_as_dict


def committees(request, state):
    chambers = get_chambers_from_abbr(state)

    committees = [
        org_as_dict(c)
        for c in Organization.objects.select_related("parent")
        .filter(Q(parent__in=chambers), classification="committee")
        .annotate(member_count=Count("memberships", filter=Q(memberships__end_date="")))
    ]
    chambers = {c.classification: c.name for c in chambers}

    return render(
        request,
        "public/views/committees.html",
        {
            "state": state,
            "state_nav": "committees",
            "chambers": chambers,
            "committees": committees,
        },
    )


def _role_sort_key(membership):
    return (membership.role.lower() == "member", membership.role)


def committee(request, state, committee_id):
    ocd_org_id = decode_uuid(committee_id, "organization")
    org = get_object_or_404(Organization.objects.all(), pk=ocd_org_id)

    # canonicalize the URL
    canonical_url = pretty_url(org)
    if request.path != canonical_url:
        return redirect(canonical_url, permanent=True)

    # because there are memberships without person records, we need to do this
    # piecemeal, we'll grab the people and memberships separately and combine them
    memberships = sorted(
        org.memberships.filter(end_date="").select_related("post"), key=_role_sort_key
    )

    members = {
        p.id: p
        for p in Person.objects.filter(memberships__in=memberships)
        .annotate(committee_role=F("memberships__role"))
        .prefetch_related(
            "memberships", "memberships__organization", "memberships__post"
        )
    }

    for membership in memberships:
        if membership.person_id:
            membership.member = members[membership.person_id]

    return render(
        request,
        "public/views/committee.html",
        {
            "state": state,
            "state_nav": "committees",
            "committee": org,
            "memberships": memberships,
        },
    )
