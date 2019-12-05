from django.urls import path
from django.views.generic.base import RedirectView

redirects = [
    ("api/", "https://docs.openstates.org/en/latest/api/index.html"),
    ("api/metadata/", "https://docs.openstates.org/en/latest/api/metadata.html"),
    ("api/bills/", "https://docs.openstates.org/en/latest/api/bills.html"),
    ("api/committees/", "https://docs.openstates.org/en/latest/api/committees.html"),
    ("api/legislators/", "https://docs.openstates.org/en/latest/api/legislators.html"),
    ("api/events/", "https://docs.openstates.org/en/latest/api/events.html"),
    ("api/districts/", "https://docs.openstates.org/en/latest/api/districts.html"),
    ("contributing/", "https://docs.openstates.org/en/latest/contributing/index.html"),
    ("csv_downloads/", "https://docs.openstates.org/en/latest/data/legacy-csv.html"),
    ("downloads/", "https://docs.openstates.org/en/latest/data/index.html"),
    ("methodology/", "https://docs.openstates.org/en/latest/infrastructure/index.html"),
    (
        "categorization/",
        "https://docs.openstates.org/en/latest/api/categorization.html",
    ),
    # old flatpages
    ("funding/", "/donate/"),
    ("contact/", "/about/"),
]

urlpatterns = [
    path(from_url, RedirectView.as_view(url=to_url, permanent=True))
    for from_url, to_url in redirects
]
