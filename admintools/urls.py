from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^admintools/$', views.overview, name='overview'),
    url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/$', views.jurisdiction_intro, name='jurisdiction_intro'),
]
