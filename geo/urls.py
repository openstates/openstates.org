from django.conf.urls import url
from .views import division_list, division_detail


urlpatterns = [
    url(r"^divisions/$", division_list),
    url(r"^(?P<pk>ocd-division/.+)/$", division_detail),
]
