from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from simplekeys.models import Key


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
