from django.conf.urls import url, include
from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from simplekeys.views import RegistrationView, ConfirmationView
from graphapi.views import KeyedGraphQLView
from graphapi.middleware import QueryProtectionMiddleware

urlpatterns = [
    path("djadmin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    url("", include("geo.urls")),
    url(r"^api/v1/", include("v1.urls")),
    url(
        r"^api/register/$",
        RegistrationView.as_view(
            confirmation_url="/api/confirm/",
            email_subject="Open States API Key Registration",
            redirect="/api/registered/",
        ),
    ),
    url(r"^api/confirm/$", ConfirmationView.as_view()),
    url(
        r"^graphql",
        csrf_exempt(
            KeyedGraphQLView.as_view(
                graphiql=True, middleware=[QueryProtectionMiddleware(5000)]
            )
        ),
    ),
    url("", include("public.urls")),
    url("", include("openstates.redirects")),
]


if settings.DEBUG:
    from django.views.defaults import page_not_found, server_error

    urlpatterns += [
        url(r"^404/$", page_not_found, {"exception": None}),
        url(r"^500/$", server_error),
        # url(r'^silk/', include('silk.urls', namespace='silk')),
    ]
