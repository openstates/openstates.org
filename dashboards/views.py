from collections import defaultdict, Counter
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, F
from django.contrib.auth.models import User
from django.shortcuts import render
from allauth.socialaccount.models import SocialAccount
from profiles.models import Subscription, Notification, UsageReport, Profile, KEY_TIERS

from utils.common import abbr_to_jid, sessions_with_bills, states
from utils.orgs import get_chambers_from_abbr
from dashboards.models import DataQualityReport
from openstates.data.models import LegislativeSession


def dqr_listing(request):
    state_dqr_data = {}

    for state in states:
        session = sessions_with_bills(abbr_to_jid(state.abbr))
        abbr = state.abbr.lower()
        lower_dashboard = None
        upper_dashboard = None
        session_name = ""
        if len(session) > 0:
            dashboards = DataQualityReport.objects.filter(session=session[0])
            if dashboards.count() > 0:
                session_name = session[0].name
                # Nebraska only has one legislature
                if abbr == "ne" or abbr == "dc":
                    upper_dashboard = dashboards.get(
                        session=session[0], chamber="legislature"
                    )
                else:
                    try:
                        lower_dashboard = dashboards.get(
                            session=session[0], chamber="lower"
                        )
                    except DataQualityReport.DoesNotExist:
                        pass
                    try:
                        upper_dashboard = dashboards.get(
                            session=session[0], chamber="upper"
                        )
                    except DataQualityReport.DoesNotExist:
                        pass

        state_dqr_data[abbr] = {
            "state": state.name,
            "session_name": session_name,
            "lower_dashboard": lower_dashboard,
            "upper_dashboard": upper_dashboard,
        }

    return render(
        request, "dashboards/dqr_listing.html", {"state_dqr_data": state_dqr_data}
    )


def dq_overview(request, state):
    jid = abbr_to_jid(state)
    all_sessions = sessions_with_bills(jid)
    dashboards = []
    session = "Dashboards Not Generated Yet"
    if all_sessions:
        session = all_sessions[0]
        dashboards = DataQualityReport.objects.filter(session=session)

    chambers = get_chambers_from_abbr(state)
    context = {
        "state": state,
        "chambers": chambers,
        "session": session,
        "all_sessions": all_sessions,
        "dashboards": dashboards,
    }

    return render(request, "dashboards/dqr_page.html", context)


def dq_overview_session(request, state, session):
    jid = abbr_to_jid(state)
    all_sessions = sessions_with_bills(jid)

    session = LegislativeSession.objects.get(identifier=session, jurisdiction_id=jid)

    dashboards = DataQualityReport.objects.filter(session=session)

    chambers = get_chambers_from_abbr(state)
    context = {
        "state": state,
        "chambers": chambers,
        "session": session,
        "all_sessions": all_sessions,
        "dashboards": dashboards,
    }

    return render(request, "dashboards/dqr_page.html", context)


@user_passes_test(lambda u: u.is_superuser)
def user_overview(request):
    bill_subscriptions = Subscription.objects.filter(bill_id__isnull=False).count()
    query_subscriptions = Subscription.objects.exclude(query="").count()
    users_by_day = list(
        User.objects.extra(select={"day": "date(date_joined)"})
        .values("day")
        .annotate(Count("id"))
        .order_by("day")
        .filter(date_joined__gte="2020-01-01")
    )

    # get counts by each provider (ignore small % with multiple providers)
    providers = list(
        SocialAccount.objects.values(name=F("provider")).annotate(value=Count("id"))
    )
    # append the number of users that only have an OS-account
    providers.append(
        {
            "name": "openstates",
            "value": User.objects.exclude(
                id__in=SocialAccount.objects.values("user_id")
            ).count(),
        }
    )

    active_users = list(
        User.objects.annotate(sub_count=Count("subscriptions"))
        .values(
            "id",
            "profile__subscription_emails_html",
            "profile__subscription_frequency",
            "sub_count",
        )
        .filter(sub_count__gt=0)
    )

    # show what users prefer
    frequencies = {"w": 0, "d": 0}
    for user in active_users:
        frequencies[user["profile__subscription_frequency"]] += 1
    frequencies = [
        {"name": "weekly", "value": frequencies["w"]},
        {"name": "daily", "value": frequencies["d"]},
    ]

    notifications_by_day = list(
        Notification.objects.extra(select={"day": "date(sent)"})
        .values("day")
        .annotate(Count("id"))
        .order_by("day")
    )

    context = {
        "user_count": User.objects.count(),
        "subscriber_count": len(active_users),
        "bill_subscriptions": bill_subscriptions,
        "query_subscriptions": query_subscriptions,
        "users_by_day": users_by_day,
        "providers": providers,
        "notifications_by_day": notifications_by_day,
        "email_frequencies": frequencies,
    }
    return render(request, "dashboards/users.html", {"context": context})


def _counter_to_chartdata(counter):
    """ restructure data from a format like "date -> value -> num"
        to "{date: date, value1: num1, value2: num2}"
        for use in charts
    """
    ret_data = []
    for date, subcounter in counter.items():
        cur_item = {"date": date}
        for k, v in subcounter.items():
            cur_item[k] = v
        ret_data.append(cur_item)
    return sorted(ret_data, key=lambda x: x["date"])


@user_passes_test(lambda u: u.is_superuser)
def api_overview(request):
    endpoint_usage = defaultdict(lambda: defaultdict(int))
    key_usage = defaultdict(lambda: defaultdict(int))
    key_totals = Counter()
    all_keys = set()

    reports = list(UsageReport.objects.all().select_related("profile__user"))
    for report in reports:
        date = str(report.date)
        key = f"{report.profile.api_key} - {report.profile.user.email}"
        endpoint_usage[date][report.endpoint] += report.calls
        key_usage[date][key] += report.calls
        key_totals[key] += report.calls
        all_keys.add(key)

    context = {
        "endpoint_usage": _counter_to_chartdata(endpoint_usage),
        "key_usage": _counter_to_chartdata(key_usage),
        "most_common": key_totals.most_common(),
        "key_tiers": list(KEY_TIERS.values()),
        "total_keys": Profile.objects.exclude(
            api_tier__in=("inactive", "suspended")
        ).count(),
        "active_keys": len(all_keys),
    }

    return render(request, "dashboards/api.html", {"context": context})
