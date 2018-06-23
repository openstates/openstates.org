from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^report/$', views.report_issue, name='report'),
    
]