from django.conf.urls import url, include
# from django.conf import settings
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView


urlpatterns = [
    url(r'^djadmin/', admin.site.urls),
    url(r'^djadmin/', include('opencivicdata.core.admin.urls')),
    url('', include('boundaries.urls')),
    url('', include('geo.urls')),
    url(r'^api/v1/', include('v1.urls')),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    # url(r'^public/', include('public.urls')),
]


# if settings.DEBUG:
#     urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
