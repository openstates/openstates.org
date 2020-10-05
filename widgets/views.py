from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseServerError
from .models import WidgetConfig, WidgetType


def index(request):
    your_widgets = list(WidgetConfig.objects.filter(owner=request.user))

    return render(
        request,
        "index.html",
        {"your_widgets": your_widgets},
    )


def widget_view(request, uuid):
    config = get_object_or_404(WidgetConfig, pk=uuid)

    if config.widget_type == WidgetType.STATE_LEGISLATORS:
        return render(request, "state_legislators.html", {})
    else:
        return HttpResponseServerError("Invalid Widget Type")
