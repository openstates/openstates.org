from django.conf.urls import url, include
from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from simplekeys.views import ConfirmationView
from graphapi.views import KeyedGraphQLView
from graphapi.middleware import QueryProtectionMiddleware
from bulk.views import bulk_csv_list

urlpatterns = [
    path("djadmin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", include("profiles.urls")),
    url("", include("geo.urls")),
    url(r"^api/v1/", include("v1.urls")),
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
    path("bulk/csv/", bulk_csv_list),
]


if settings.DEBUG:
    from django.views.defaults import page_not_found, server_error

    urlpatterns += [
        url(r"^404/$", page_not_found, {"exception": None}),
        url(r"^500/$", server_error),
        # url(r'^silk/', include('silk.urls', namespace='silk')),
    ]
