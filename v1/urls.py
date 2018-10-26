from django.urls import path, re_path
from . import views

urlpatterns = [
    # (r'^v1/metadata/$', all_metadata_handler),
    re_path(r'^metadata/(?P<abbr>[a-zA-Z-]+)/$', views.state_metadata),

    # (r'^bills/(?P<abbr>[a-zA-Z-]+)/(?P<session>.+)/'
    #     r'(?P<chamber>upper|lower)/(?P<bill_id>.+)/$', bill_handler),
    # (r'^bills/(?P<abbr>[a-zA-Z-]+)/(?P<session>.+)/'
    #     r'(?P<bill_id>.+)/$', bill_handler),
    # (r'^bills/(?P<billy_bill_id>[A-Z-]+B\d{8})/', bill_handler),
    # (r'^bills/$', bill_search_handler),

    # (r'^legislators/(?P<id>[A-Z-]+L\d{6})/$', legislator_handler),
    # (r'^legislators/$', legsearch_handler),
    # (r'^legislators/geo/$', legislator_geo_handler),

    re_path(r'^committees/(?P<id>[A-Z-]+C\d{6})/$', views.item_404),
    re_path(r'^committees/$', views.empty_list),
    re_path(r'^events/$', views.empty_list),
    re_path(r'^events/(?P<id>[A-Z-]+E\d{8})/$', views.item_404),

    # (r'districts/(?P<abbr>[a-zA-Z-]+)/$',
    #     district_handler),
    # (r'districts/(?P<abbr>[a-zA-Z-]+)/(?P<chamber>upper|lower)/$',
    #     district_handler),
    # (r'districts/boundary/(?P<boundary_id>.+)/$', boundary_handler),
]
