from django.contrib import admin
from django.urls import path
from widgets import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index),
    path("w/<uuid:uuid>", views.widget_view),
]
