from django.urls import path
from . import views

urlpatterns = [
    path("", views.overview),
    path("session-csv/", views.bulk_session_list, {"data_type": "csv"}),
    path("session-json/", views.bulk_session_list, {"data_type": "json"}),
]
