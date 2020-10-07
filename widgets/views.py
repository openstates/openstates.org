import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseServerError, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import WidgetConfig, WidgetType


def index(request):
    if request.user.is_authenticated:
        your_widgets = list(WidgetConfig.objects.filter(owner=request.user))
    else:
        your_widgets = []

    return render(request, "index.html", {"your_widgets": your_widgets})


@login_required
def configure(request):
    if request.method == "GET":
        widget_type_name = None
        widget_type = request.GET.get("new")

        if widget_type == WidgetType.STATE_LEGISLATORS:
            widget_type_name = "State Legislator Lookup"

        if not widget_type_name:
            return HttpResponseServerError("Invalid Widget Type")

        return render(
            request,
            "configure.html",
            {"widget_type": widget_type, "widget_type_name": widget_type_name,},
        )
    elif request.method == "POST":
        body = json.loads(request.body)
        name = body.pop("name")
        widget_type = body.pop("widgetType")
        wc = WidgetConfig(
            owner=request.user, name=name, widget_type=widget_type, settings=body
        )
        wc.save()
        return JsonResponse({"id": wc.id})


def widget_view(request, uuid):
    config = get_object_or_404(WidgetConfig, pk=uuid)
    combined_config = dict(
        **config.settings,
        openstates_api_key=settings.OPENSTATES_API_KEY,
        mapbox_access_token=settings.MAPBOX_ACCESS_TOKEN
    )

    if config.widget_type == WidgetType.STATE_LEGISLATORS:
        return render(request, "state_legislators.html", {"config": combined_config})
    else:
        return HttpResponseServerError("Invalid Widget Type")
