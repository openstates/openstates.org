from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    primary = request.user.emailaddress_set.get(primary=True)
    return render(request, "account/profile.html", {"primary_email": primary})
