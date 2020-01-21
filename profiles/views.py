from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import redirect, render
from simplekeys.models import Key
from .models import Subscription, Profile


class PermissionException(Exception):
    pass


def _ensure_feature_flag(user, perm="feature_subscriptions"):
    try:
        if getattr(user.profile, perm):
            return True
    except Profile.DoesNotExist:
        pass
    raise PermissionException(f"{user} does not have {perm}")


@login_required
def profile(request):
    primary = request.user.emailaddress_set.get(primary=True)

    # only get their key if the email is verified
    key = None
    if primary.verified:
        try:
            key = Key.objects.get(email=primary.email)
        except Key.DoesNotExist:
            pass

    subscriptions = request.user.subscriptions.filter(active=True).order_by(
        "-created_at"
    )

    return render(
        request,
        "account/profile.html",
        {"primary_email": primary, "key": key, "subscriptions": subscriptions},
    )


@login_required
@require_POST
def delete_subscription(request):
    print(request.POST)
    try:
        sub = Subscription.objects.get(
            user=request.user, pk=request.POST["subscription_id"]
        )
        sub.delete()
        messages.info(request, f"Deleted subscription: {sub.pretty}")
    except Subscription.DoesNotExist:
        pass
    return redirect("/accounts/profile/")


@login_required
@require_POST
def add_search_subscription(request):
    _ensure_feature_flag(request.user)
    sub, created = Subscription.objects.get_or_create(
        user=request.user,
        query=request.POST["query"],
        state=request.POST["state"],
        chamber=request.POST.get("chamber", ""),
        classification=request.POST.get("classification", ""),
        subjects=request.POST.getlist("subjects"),
        status=request.POST.getlist("status"),
        sponsor_id=request.POST.get("sponsor_id"),
    )
    if created:
        messages.info(request, f"Created new subscription: {sub.pretty}")
    return redirect("/accounts/profile/")


@login_required
@require_POST
def add_sponsor_subscription(request):
    _ensure_feature_flag(request.user)
    sub, created = Subscription.objects.get_or_create(
        user=request.user,
        sponsor_id=request.POST["sponsor_id"],
        query="",
        subjects=[],
        status=[],
    )
    if created:
        messages.info(request, f"Created new subscription: {sub.pretty}")
    return redirect("/accounts/profile/")


@login_required
@require_POST
def add_bill_subscription(request):
    _ensure_feature_flag(request.user)
    sub, created = Subscription.objects.get_or_create(
        user=request.user,
        bill_id=request.POST["bill_id"],
        query="",
        subjects=[],
        status=[],
    )
    if created:
        messages.info(request, f"Created new subscription: {sub.pretty}")
    return redirect("/accounts/profile/")
