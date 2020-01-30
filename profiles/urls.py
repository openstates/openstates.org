from django.urls import path
from .views import (
    profile,
    unsubscribe,
    bill_subscription,
    add_search_subscription,
    add_sponsor_subscription,
    deactivate_subscription,
)

urlpatterns = [
    path("", profile),
    path("unsubscribe/", unsubscribe),
    path("bill_sub/", bill_subscription),
    path("add_sponsor_sub/", add_sponsor_subscription),
    path("add_search_sub/", add_search_subscription),
    path("deactivate_sub/", deactivate_subscription),
]
