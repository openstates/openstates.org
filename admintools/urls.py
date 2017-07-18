from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^admintools/$', views.overview, name='overview'),

    url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/view-all-patches/$',
        views.list_all_person_patches, name="list_all_person_patches"),

    url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/review-patches/$',
        views.review_person_patches, name="review_person_patches"),

    url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/$', views.jurisdiction_intro,
        name='jurisdiction_intro'),

    # must be above 'list_issue_objects' to avoid 'related_class'
    url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/session-id/'
        '(?P<identifier>.*)$', views.legislative_session_info,
        name="legislative_session_info"),

    url(r'^admintools/(?P<jur_name>[a-zA-Z\s]*)/(?P<related_class>[-\w]+)/'
        '(?P<issue_slug>[-\w]+)$',
        views.list_issue_objects, name='list_issue_objects'),

    url(r'^admintools/(?P<issue_slug>[-\w]+)/(?P<jur_name>[a-zA-Z\s]*)/$',
        views.person_resolve_issues, name='person_resolve_issues')
]
