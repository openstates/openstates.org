from collections import Counter
import feedparser
from django.db.models import Min, Max, Sum
from django.shortcuts import render
from django.core.cache import cache
from opencivicdata.legislative.models import Bill
from opencivicdata.core.models import Organization
from utils.common import abbr_to_jid, states, sessions_with_bills
from ..models import PersonProxy


def styleguide(request):
    return render(request, "public/views/styleguide.html")


def _get_latest_updates():
    RSS_FEED = "https://blog.openstates.org/feed"

    feed = feedparser.parse(RSS_FEED)
    return [{"title": entry.title, "link": entry.link} for entry in feed.entries][:3]


def _get_random_bills():
    return (
        Bill.objects.all().order_by("-updated_at").prefetch_related("sponsorships")[:3]
    )


def home(request):
    # cache these to try to keep the homepage as cheap as possible
    cache_time = 60 * 60 * 24  # cache for a full day
    updates = cache.get_or_set("homepage-blog-updates", _get_latest_updates, cache_time)
    recent_bills = cache.get_or_set("homepage-bills", _get_random_bills, cache_time)

    context = {"states": states, "recent_bills": recent_bills, "blog_updates": updates}
    return render(request, "public/views/home.html", context)


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
        parties = []
        titles = []
        for legislator in legislators:
            if legislator.current_role["chamber"] == chamber.classification:
                parties.append(legislator.current_role["party"])
                titles.append(legislator.current_role["role"])

        chamber.parties = dict(Counter(parties))
        chamber.title = titles[0]
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

    all_sessions = sessions_with_bills(jid)

    return render(
        request,
        "public/views/state.html",
        {
            "state": state,
            "state_nav": "overview",
            "legislature": legislature,
            "chambers": chambers,
            "chambers_json": {c.classification: c.name for c in chambers},
            "recently_introduced_bills": recently_introduced_bills,
            "recently_passed_bills": recently_passed_bills,
            "all_sessions": all_sessions,
        },
    )
