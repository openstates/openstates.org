import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import WidgetConfig, WidgetType
from rrl import RateLimiter, Tier, RateLimitExceeded


limiter = RateLimiter(
    prefix="widgets",
    tiers=[Tier("default", 120, 0, 2000)],
    use_redis_time=False,
    track_daily_usage=True,
)


def index(request):
    if request.user.is_authenticated:
        your_widgets = list(WidgetConfig.objects.filter(owner=request.user))
    else:
        your_widgets = []

    return render(request, "index.html", {"your_widgets": your_widgets})


@ensure_csrf_cookie
@login_required
def configure(request):
    if request.method == "GET":
        widget_type_name = None
        widget_type = request.GET.get("new")

        if widget_type == WidgetType.STATE_LEGISLATORS:
            widget_type_name = "State Legislator Lookup"

        if not widget_type_name:
            return HttpResponse("Invalid Widget Type", status=500)

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


@login_required
def usage(request, uuid):
    config = get_object_or_404(WidgetConfig, pk=uuid)
    if request.user != config.owner:
        return HttpResponse("Permission Denied", status=403)
    usage = limiter.get_usage_since("widgets", uuid, config.created_at.date())
    return render(
        request, "usage.html", {"config": config, "usage": usage, "daily_limit": 2000}
    )


def widget_view(request, uuid):
    config = get_object_or_404(WidgetConfig, pk=uuid)
    try:
        limiter.check_limit("widgets", uuid, "default")
    except RateLimitExceeded as e:
        return HttpResponse(str(e), status=429)
    combined_config = dict(
        **config.settings,
        openstates_api_key=settings.OPENSTATES_API_KEY,
        mapbox_access_token=settings.MAPBOX_ACCESS_TOKEN
    )

    if config.widget_type == WidgetType.STATE_LEGISLATORS:
        return render(request, "state_legislators.html", {"config": combined_config})
    else:
        return HttpResponse("Invalid Widget Type", status=500)
