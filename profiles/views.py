from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from simplekeys.models import Key
from .models import Subscription


class PermissionException(Exception):
    pass


def _ensure_feature_flag(user, perm="feature_subscriptions"):
    if user.profile and getattr(user.profile, perm):
        return True
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

    messages.info(
        request,
        "Accounts are currently a beta feature, more functionality is coming soon!",
    )
    return render(
        request, "account/profile.html", {"primary_email": primary, "key": key}
    )


@login_required
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
        messages.info(request, f"Created new subscription for '{sub.query}'")
    return redirect("/accounts/profile/")


@login_required
def add_sponsor_subscription(request):
    _ensure_feature_flag(request.user)
    sub, created = Subscription.objects.get_or_create(
        user=request.user, query="", sponsor_id=request.POST["sponsor_id"]
    )
    if created:
        messages.info(request, f"Created new subscription for sponsor '{sub.sponsor}'")
    return redirect("/accounts/profile/")


@login_required
def add_bill_subscription(request):
    _ensure_feature_flag(request.user)
    sub, created = Subscription.objects.get_or_create(
        user=request.user, query="", bill_id=request.POST["bill_id"]
    )
    if created:
        messages.info(request, f"Created new subscription for bill '{sub.bill}'")
    return redirect("/accounts/profile/")
