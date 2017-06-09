from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^admintools/$', views.overview, name='overview'),
]
