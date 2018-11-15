from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^metadata/$', views.all_metadata),
    re_path(r'^metadata/(?P<abbr>[a-zA-Z-]+)/$', views.state_metadata),

    re_path(r'^bills/(?P<abbr>[a-zA-Z-]+)/(?P<session>.+)/'
            r'(?P<chamber>upper|lower)/(?P<bill_id>.+)/$', views.bill_detail),
    re_path(r'^bills/(?P<abbr>[a-zA-Z-]+)/(?P<session>.+)/'
            r'(?P<bill_id>.+)/$', views.bill_detail),
    re_path(r'^bills/(?P<billy_bill_id>[A-Z-]+B\d{8})/', views.bill_detail),
    re_path(r'^bills/$', views.bill_list),

    re_path(r'^legislators/(?P<id>[A-Z-]+L\d{6})/$', views.legislator_detail),
    re_path(r'^legislators/$', views.legislator_list),
    re_path(r'^legislators/geo/$', views.legislator_list, {'geo': True}),

    re_path(r'districts/(?P<abbr>[a-zA-Z-]+)/$', views.district_list),
    re_path(r'districts/(?P<abbr>[a-zA-Z-]+)/(?P<chamber>upper|lower)/$', views.district_list),

    # removed views
    re_path(r'^committees/(?P<id>[A-Z-]+C\d{6})/$', views.item_404),
    re_path(r'^committees/$', views.empty_list),
    re_path(r'^events/$', views.empty_list),
    re_path(r'^events/(?P<id>[A-Z-]+E\d{8})/$', views.item_404),
]
