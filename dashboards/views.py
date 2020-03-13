from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, F
from django.contrib.auth.models import User
from django.shortcuts import render
from allauth.socialaccount.models import SocialAccount
from profiles.models import Subscription, Notification


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
