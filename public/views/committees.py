from django.shortcuts import render
from django.db.models import Q, Count
from utils.orgs import get_chambers_from_abbr
from ..models import OrganizationProxy


def committees(request, state):
    chambers = get_chambers_from_abbr(state)

    committees = [c.as_dict() for c in
                  OrganizationProxy.objects
                  .select_related("parent")
                  .filter(Q(parent__in=chambers), classification="committee")
                  .annotate(member_count=Count('memberships', filter=Q(memberships__end_date="")))
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


def committee(request, state):
    return render(request, "public/views/committee.html", {"state": state})
