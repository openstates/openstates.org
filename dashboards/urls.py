from django.urls import path
from .views import user_overview, api_overview, dq_overview

urlpatterns = [
    path("users/", user_overview),
    path("api/", api_overview),
    path("dq_dashboard/", dq_overview),
]
