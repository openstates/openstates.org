from django.conf.urls import url
from . import views

urlpatterns = [

    # all the urls starting with `jur_id` should have some manual string
    # identifier after them other they will get redirected to
    # `jurisdiction_intro` page causing `jurisdiction_id` not mathced error.

    url(r'^admintools/$', views.overview, name='overview'),

    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/all-patches/$',
        views.list_all_person_patches, name="list_all_person_patches"),

    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/create-patch/$',
        views.create_person_patch, name="create_person_patch"),

    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/review-patches/$',
        views.review_person_patches, name="review_person_patches"),

    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/retire-legislators/$',
        views.retire_legislators, name="retire_legislators"),

    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/all-retired-legislators/$',
        views.list_retired_legislators, name="list_retired_legislators"),

    # must be above 'list_issue_objects' & 'jurisdiction_intro'
    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/session-id/'
        '(?P<identifier>.*)/$', views.legislative_session_info,
        name="legislative_session_info"),

    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/intro$',
        views.jurisdiction_intro, name='jurisdiction_intro'),

    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/_(?P<related_class>[-\w]+)_/'
        '(?P<issue_slug>[-\w]+)/$',
        views.list_issue_objects, name='list_issue_objects'),

    # must be above `name_resolution_tool`
    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/create-patch/'
        '(?P<issue_slug>[-\w]+)/$',
        views.person_resolve_issues, name='person_resolve_issues'),

    url(r'^admintools/(?P<jur_id>[\w\-\:\/]+)/(?P<category>[-\w]+)/$',
        views.name_resolution_tool, name='name_resolution_tool')

]
