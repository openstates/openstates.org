from django.urls import path
from .views import user_overview

urlpatterns = [
    path("users/", user_overview),
]
