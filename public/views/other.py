from collections import Counter
import feedparser
from django.db.models import Min, Max, Sum, Count
from django.shortcuts import render, redirect
from opencivicdata.legislative.models import Bill, LegislativeSession
from opencivicdata.core.models import Organization
from utils.common import abbr_to_jid, states
from ..models import PersonProxy


def styleguide(request):
    return render(request, "public/views/styleguide.html")


def home(request):
    RSS_FEED = "https://blog.openstates.org/feed"

    feed = feedparser.parse(RSS_FEED)
    updates = [
        {
            "title": entry.title,
            "link": entry.link,
        }
        for entry in feed.entries
    ]

    context = {
        "states": states,
        "recent_bills": Bill.objects.all()[:3],
        "blog_updates": updates,
    }
    return render(request, "public/views/home.html", context)


def unslash(request, *args, **kwargs):
    return redirect(request.path.rstrip("/"), permanent=True)


def state(request, state):
    RECENTLY_INTRODUCED_BILLS_TO_SHOW = 4
    RECENTLY_PASSED_BILLS_TO_SHOW = 4

    jid = abbr_to_jid(state)

    # we need basically all of the orgs, so let's just do one big query for them
    legislature = None
    committee_counts = Counter()
    chambers = []

    organizations = Organization.objects.filter(jurisdiction_id=jid).annotate(
        seats=Sum("posts__maximum_memberships")
    )

    for org in organizations:
        if org.classification == "legislature":
            legislature = org
        elif org.classification in ("upper", "lower"):
            chambers.append(org)
        elif org.classification == "committee":
            committee_counts[org.parent.classification] += 1

    # unicameral
    if not chambers:
        chambers = [legislature]

    # legislators
    legislators = PersonProxy.get_current_legislators_with_roles(chambers)

    for chamber in chambers:
        parties = [
            legislator.current_role["party"]
            for legislator in legislators
            if legislator.current_role["chamber"] == chamber.classification
        ]
        chamber.parties = dict(Counter(parties))
        if chamber.seats - len(legislators) > 0:
            chamber.parties["Vacancies"] = chamber.seats - len(legislators)

        chamber.committee_count = committee_counts[chamber.classification]

    # bills
    bills = Bill.objects.filter(from_organization__in=chambers).prefetch_related(
        "sponsorships"
    )

    recently_introduced_bills = list(
        bills.filter(actions__isnull=False)
        .annotate(introduced_date=Min("actions__date"))
        .order_by("-introduced_date")[:RECENTLY_INTRODUCED_BILLS_TO_SHOW]
    )

    recently_passed_bills = list(
        bills.filter(actions__classification__contains=["passage"])
        .annotate(passed_date=Max("actions__date"))
        .order_by("-passed_date")[:RECENTLY_PASSED_BILLS_TO_SHOW]
    )

    all_sessions = (
        LegislativeSession.objects.filter(jurisdiction_id=jid)
        .annotate(bill_count=Count("bills"))
        .filter(bill_count__gt=0)
        .order_by("-end_date", "-identifier")
    )

    return render(
        request,
        "public/views/state.html",
        {
            "state": state,
            "state_nav": "overview",
            "legislature": legislature,
            "chambers": chambers,
            "recently_introduced_bills": recently_introduced_bills,
            "recently_passed_bills": recently_passed_bills,
            "all_sessions": all_sessions,
        },
    )
