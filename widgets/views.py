from django.shortcuts import render


def widget_view(request, uuid):
    return render(request, "state_legislators.html", {})
