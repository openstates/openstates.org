from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]


# if settings.DEBUG:
#     urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
