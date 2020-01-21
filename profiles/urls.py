from django.urls import path
from .views import (
    add_bill_subscription,
    add_search_subscription,
    add_sponsor_subscription,
)

urlpatterns = [
    path("add_bill_sub/", add_bill_subscription),
    path("add_search_sub/", add_search_subscription),
    path("add_sponsor_sub/", add_sponsor_subscription),
]
