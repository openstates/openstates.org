from django.conf.urls import url
from . import views

urlpatterns = [

    # all the urls starting with `jur_id` should have some manual string
    # identifier after them otherwise they will get redirected to
    # `jurisdiction_overview` page resulting `jurisdiction_id` not matched error.

    # overview
    url(r'^$', views.overview, name='overview'),

    url(r'^(?P<jur_id>[\w\-\:\/]+)/overview/$',
        views.jurisdiction_overview, name='jurisdiction_overview'),

    url(r'^(?P<jur_id>[\w\-\:\/]+)/session-id/'
        '(?P<identifier>.*)/$', views.legislative_session_info,
        name="legislative_session_info"),

    url(r'^(?P<jur_id>[\w\-\:\/]+)/_(?P<related_class>[-\w]+)_/'
        '(?P<issue_slug>[-\w]+)/$',
        views.list_issue_objects, name='list_issue_objects'),

    # patches
    url(r'^(?P<jur_id>[\w\-\:\/]+)/all-patches/$',
        views.list_all_person_patches, name="list_all_person_patches"),

    url(r'^(?P<jur_id>[\w\-\:\/]+)/create-patch/$',
        views.create_person_patch, name="create_person_patch"),

    url(r'^(?P<jur_id>[\w\-\:\/]+)/review-patches/$',
        views.review_person_patches, name="review_person_patches"),

    url(r'^(?P<jur_id>[\w\-\:\/]+)/create-patch/'
        '(?P<issue_slug>[-\w]+)/$',
        views.person_resolve_issues, name='person_resolve_issues'),

    url(r'^(?P<jur_id>[\w\-\:\/]+)/ignored-issues/'
        '(?P<issue_slug>[-\w]+)/(?P<action>[-\w]+)/$',
        views.dataquality_exceptions, name='dataquality_exceptions'),

    # retirement
    url(r'^(?P<jur_id>[\w\-\:\/]+)/retire-legislators/$',
        views.retire_legislators, name="retire_legislators"),

    url(r'^(?P<jur_id>[\w\-\:\/]+)/all-retired-legislators/$',
        views.list_retired_legislators, name="list_retired_legislators"),

    # name resolution
    url(r'^(?P<jur_id>[\w\-\:\/]+)/(?P<category>[-\w]+)/$',
        views.name_resolution_tool, name='name_resolution_tool'),
]
