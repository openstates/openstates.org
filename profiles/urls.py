from django.urls import path
from .views import (
    profile,
    request_key,
    unsubscribe,
    bill_subscription,
    add_search_subscription,
    add_sponsor_subscription,
    deactivate_subscription,
    admin_overview,
)

urlpatterns = [
    path("", profile),
    path("request_key/", request_key),
    path("unsubscribe/", unsubscribe),
    path("bill_sub/", bill_subscription),
    path("add_sponsor_sub/", add_sponsor_subscription),
    path("add_search_sub/", add_search_subscription),
    path("deactivate_sub/", deactivate_subscription),
    # admin stuff
    path("overview/", admin_overview),
]
