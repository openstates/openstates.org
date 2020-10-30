from django.urls import path
from django.views.generic.base import RedirectView

redirects = [
    ("api/register/", "/accounts/login/"),
    ("api/", "https://docs.openstates.org/en/latest/api/index.html"),
    ("api/metadata/", "https://docs.openstates.org/en/latest/api/metadata.html"),
    ("api/bills/", "https://docs.openstates.org/en/latest/api/bills.html"),
    ("api/legislators/", "https://docs.openstates.org/en/latest/api/legislators.html"),
    ("api/districts/", "https://docs.openstates.org/en/latest/api/districts.html"),
    ("contributing/", "https://docs.openstates.org/en/latest/contributing/index.html"),
    ("methodology/", "https://docs.openstates.org/en/latest/infrastructure/index.html"),
    (
        "categorization/",
        "https://docs.openstates.org/en/latest/api/categorization.html",
    ),
    (
        "mailing-list/",
        "https://cdn.forms-content.sg-form.com/b8d934d4-7b67-11ea-a680-1a7f462d56d4",
    ),
    # old flatpages
    ("funding/", "/donate/"),
    ("contact/", "/about/"),
    ("bulk/csv/", "/data/session-csv/"),
    ("csv_downloads/", "/data/session-csv/"),
    ("downloads/", "/data/"),
    # bounce to widgets
    ("widgets/", "https://widgets.openstates.org"),
]

urlpatterns = [
    path(from_url, RedirectView.as_view(url=to_url, permanent=False))
    for from_url, to_url in redirects
]
