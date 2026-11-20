from django.urls import path

from .views import (
    add_search_subscription,
    add_sponsor_subscription,
    bill_subscription,
    deactivate_subscription,
    profile,
    request_key,
    unsubscribe,
)

urlpatterns = [
    path("", profile),
    path("request_key/", request_key),
    path("unsubscribe/", unsubscribe),
    path("bill_sub/", bill_subscription),
    path("add_sponsor_sub/", add_sponsor_subscription),
    path("add_search_sub/", add_search_subscription),
    path("deactivate_sub/", deactivate_subscription),
]
