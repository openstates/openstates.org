from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F
from utils.common import decode_uuid, pretty_url
from utils.orgs import get_chambers_from_abbr
from ..models import OrganizationProxy, PersonProxy


def committees(request, state):
    chambers = get_chambers_from_abbr(state)

    committees = [
        c.as_dict()
        for c in OrganizationProxy.objects.select_related("parent")
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


def _role_sort_key(member):
    return (member.committee_role.lower() == "member", member.committee_role)


def committee(request, state, committee_id):
    ocd_org_id = decode_uuid(committee_id, "organization")
    org = get_object_or_404(OrganizationProxy.objects.all(), pk=ocd_org_id)

    # canonicalize the URL
    canonical_url = pretty_url(org)
    if request.path != canonical_url:
        return redirect(canonical_url, permanent=True)

    members = sorted(
        PersonProxy.objects.filter(
            memberships__organization_id=org.id, memberships__end_date=""
        )
        .annotate(committee_role=F("memberships__role"))
        .prefetch_related(
            "memberships", "memberships__organization", "memberships__post"
        ),
        key=_role_sort_key,
    )

    return render(
        request,
        "public/views/committee.html",
        {
            "state": state,
            "state_nav": "committees",
            "committee": org,
            "committee_members": members,
        },
    )
