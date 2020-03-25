from django.urls import path
from .views import bundle_view

urlpatterns = [
    path("<str:slug>/", bundle_view),
]
