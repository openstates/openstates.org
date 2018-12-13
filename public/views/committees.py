from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, F
from utils.common import decode_uuid
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


def committee(request, state, committee_id):
    ocd_org_id = decode_uuid(committee_id, "organization")
    org = get_object_or_404(
        OrganizationProxy.objects.prefetch_related("memberships__organization"),
        pk=ocd_org_id,
    )

    members = PersonProxy.objects.filter(
        memberships__organization_id=org.id, memberships__end_date=""
    ).annotate(committee_role=F("memberships__role"))

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
