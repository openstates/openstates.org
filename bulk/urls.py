from django.urls import path
from . import views

urlpatterns = [
    path("", views.overview),
    path("session-csv/", views.bulk_csv_list),
    path("session-json/", views.bulk_json_list),
]
