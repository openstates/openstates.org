from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def profile(request):
    primary = request.user.emailaddress_set.get(primary=True)
    messages.info(
        request,
        "Accounts are currently a beta feature, more functionality is coming soon!",
    )
    return render(request, "account/profile.html", {"primary_email": primary})
