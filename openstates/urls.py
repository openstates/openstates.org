from django.conf.urls import url, include
from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from graphapi.views import KeyedGraphQLView
from graphapi.middleware import QueryProtectionMiddleware


urlpatterns = [
    path("djadmin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", include("profiles.urls")),
    path("dashboard/", include("dashboards.urls")),
    url("", include("geo.urls")),
    url(r"^api/v1/", include("v1.urls")),
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
    url("data/", include("bulk.urls")),
]


if settings.DEBUG:
    from django.views.defaults import page_not_found, server_error

    urlpatterns += [
        url(r"^404/$", page_not_found, {"exception": None}),
        url(r"^500/$", server_error),
        # url(r'^silk/', include('silk.urls', namespace='silk')),
    ]
