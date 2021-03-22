from django.urls import path
from django.views.generic.base import RedirectView

redirects = [
    ("api/register/", "/accounts/login/"),
    ("api/", "https://docs.openstates.org/en/latest/api/v3/index.html"),
    ("contributing/", "/about/contributing/"),
    ("methodology/", "/about/"),
    ("mailing-list/", "/about/"),
    ("donate/", "/about/"),
    ("funding/", "/about/"),
    ("contact/", "/about/"),
    ("bulk/csv/", "/data/session-csv/"),
    ("csv_downloads/", "/data/session-csv/"),
    ("downloads/", "/data/"),
]

urlpatterns = [
    path(from_url, RedirectView.as_view(url=to_url, permanent=False))
    for from_url, to_url in redirects
]
