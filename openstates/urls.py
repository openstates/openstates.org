from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView


urlpatterns = [
    url(r'^djadmin/', admin.site.urls),
    url(r'^djadmin/', include('opencivicdata.core.admin.urls')),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    # url(r'^public/', include('public.urls')),
    # url(r'^reports/', include('dataquality.urls'))
]


if settings.DEBUG:
    pass
#     urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
