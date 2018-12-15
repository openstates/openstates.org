from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from simplekeys.views import RegistrationView, ConfirmationView
from graphapi.views import KeyedGraphQLView
from graphapi.middleware import QueryProtectionMiddleware

urlpatterns = [
    url(r'^djadmin/', admin.site.urls),
    url('', include('geo.urls')),
    url(r'^api/v1/', include('v1.urls')),
    url(r'^api/register/$', RegistrationView.as_view(
        confirmation_url='/api/confirm/',
        email_subject='Open States API Key Registration',
    )),
    url(r'^api/confirm/$', ConfirmationView.as_view()),
    url(r'^graphql', csrf_exempt(KeyedGraphQLView.as_view(
        graphiql=True,
        middleware=[QueryProtectionMiddleware(5000)])
    )),
    url('', include('public.urls')),
    url('', include('openstates.redirects')),
]


if settings.DEBUG:
    pass
#     urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
