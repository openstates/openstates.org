from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^admintools/$', views.overview, name='overview'),
    url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/$', views.jurisdiction_intro, name='jurisdiction_intro'),
    url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/(?P<related_class>[-\w]+)/(?P<issue_slug>[-\w]+)$',
        views.list_issue_objects, name='list_issue_objects'),
]


url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/(?P<related_class>[-\w]+)/(?:(?P<issue_slug>[-\w]+))?$',
    views.list_issue_objects, name='list_issue_objects'),
