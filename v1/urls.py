from django.conf.urls import url
from .views import bill_list


urlpatterns = [
    url(r'^bills/$', bill_list),
]
