# not tests, just Django urls

from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('opencivicdata.core.admin.urls')),
    url(r'', include('opencivicdata.legislative.admin.urls')),
    url(r'', include('admintools.urls'))
]
