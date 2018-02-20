from django.urls import path, re_path

from . import views


OCD_ID_PATTERN = r'[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}'

urlpatterns = [
    path('legislators', views.legislators, name='legislators'),
    re_path(r'^legislator/(?P<legislator_id>ocd-person/{})'.format(OCD_ID_PATTERN), views.legislator, name='legislator'),
]
