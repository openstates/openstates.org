from django.urls import path, re_path

from utils.common import states

from .views import (
    api_overview,
    dq_overview,
    dq_overview_session,
    dqr_listing,
    user_overview,
)

# Only allow valid state abbreviations
state_abbrs = [s.abbr.lower() for s in states]
state_abbr_pattern = r"({})".format("|".join(state_abbrs))

urlpatterns = [
    path("users/", user_overview),
    path("api/", api_overview),
    path("dq_dashboard/", dqr_listing),
    re_path(r"^dq_overview/(?P<state>{})/$".format(state_abbr_pattern), dq_overview),
    re_path(
        r"^dq_overview/(?P<state>{})/(?P<session>[-\w ]+)/$".format(state_abbr_pattern),
        dq_overview_session,
    ),
]
