from django.urls import path
from .views import bundle_view, csv_view

urlpatterns = [
    path("<str:slug>/", bundle_view),
    path("<str:slug>/csv/", csv_view),
]
