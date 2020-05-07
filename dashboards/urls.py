from django.urls import path, re_path
from .views import user_overview, api_overview, dq_overview, dq_overview_session, dqr_listing
from utils.common import states

# Only allow valid state abbreviations
state_abbrs = [s.abbr.lower() for s in states]
state_abbr_pattern = r"({})".format("|".join(state_abbrs))

urlpatterns = [
    path("users/", user_overview),
    path("api/", api_overview),
    re_path("dq_dashboard/", dqr_listing),
    re_path(r"^dq_overview/(?P<state>{})/$".format(state_abbr_pattern), dq_overview),
    re_path(r"^dq_overview/(?P<state>{})/(?P<session>[-\w ]+)/$".format(
        state_abbr_pattern
    ), dq_overview_session),
]
