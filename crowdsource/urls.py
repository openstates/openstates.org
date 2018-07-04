from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^report/$', views.report_issue, name='report'),
    url(r'^resolve/$', views.submit_resolve, name='resolve'),
    url(r'^issues/$', views.list_issues, name='list'),
]
