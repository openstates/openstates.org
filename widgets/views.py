from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseServerError
from django.contrib.auth.decorators import login_required
from .models import WidgetConfig, WidgetType


def index(request):
    your_widgets = list(WidgetConfig.objects.filter(owner=request.user))

    return render(request, "index.html", {"your_widgets": your_widgets})


@login_required
def configure(request):
    options = None

    widget_type = request.GET.get("new")

    if widget_type == WidgetType.STATE_LEGISLATORS:
        options = {"background_color": "color", "foreground_color": "color"}
        widget_type_name = "State Legislator Lookup"

    if not options:
        return HttpResponseServerError("Invalid Widget Type")

    return render(
        request,
        "configure.html",
        {
            "widget_type": widget_type,
            "widget_type_name": widget_type_name,
            "options": options,
        },
    )


def widget_view(request, uuid):
    config = get_object_or_404(WidgetConfig, pk=uuid)

    if config.widget_type == WidgetType.STATE_LEGISLATORS:
        return render(request, "state_legislators.html", {})
    else:
        return HttpResponseServerError("Invalid Widget Type")
