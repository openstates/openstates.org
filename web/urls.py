from django.urls import path, include, re_path
from django.conf import settings
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from graphapi.views import KeyedGraphQLView
from graphapi.middleware import QueryProtectionMiddleware
from bundles.views import bundle_view


urlpatterns = [
    path("djadmin/", admin.site.urls),
    path("admin/people/", include("people_admin.urls")),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", include("profiles.urls")),
    path("dashboard/", include("dashboards.urls")),
    path("api/v1/", include("v1.urls")),
    re_path(
        "^graphql/?$",
        csrf_exempt(
            KeyedGraphQLView.as_view(
                graphiql=True, middleware=[QueryProtectionMiddleware(5000)]
            )
        ),
    ),
    path("", include("public.urls")),
    path("", include("web.redirects")),
    path("data/", include("bulk.urls")),
    path("bundles/", include("bundles.urls")),
    path("covid19/", bundle_view, {"slug": "covid19"}),
    # flatpages
    path("about/", TemplateView.as_view(template_name="flat/about.html")),
    path(
        "about/contributing/",
        TemplateView.as_view(template_name="flat/contributing.html"),
    ),
    path(
        "about/subscriptions/",
        TemplateView.as_view(template_name="flat/subscriptions.html"),
    ),
    path("tos/", TemplateView.as_view(template_name="flat/tos.html")),
    path("api/registered/", TemplateView.as_view(template_name="flat/registered.html")),
]


if settings.DEBUG:
    from django.views.defaults import page_not_found, server_error

    urlpatterns += [
        path("404/", page_not_found, {"exception": None}),
        path("500/", server_error),
        # url(r'^silk/', include('silk.urls', namespace='silk')),
    ]
