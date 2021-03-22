from django.urls import path, re_path
from utils.common import states
from .views import (
    jurisdiction_list,
    people_list,
    people_matcher,
    apply_match,
)

# Only allow valid state abbreviations
state_abbrs = [s.abbr.lower() for s in states]
state_abbr_pattern = r"({})".format("|".join(state_abbrs))

urlpatterns = [
    path("", jurisdiction_list),
    re_path(
        r"^(?P<state>{})/$".format(state_abbr_pattern),
        people_list,
        name="people_admin_list",
    ),
    re_path(
        r"^(?P<state>{})/matcher/$".format(state_abbr_pattern),
        people_matcher,
        name="people_matcher",
    ),
    re_path(
        r"^(?P<state>{})/matcher/(?P<session>[-\w ]+)/$".format(state_abbr_pattern),
        people_matcher,
        name="session_people_matcher",
    ),
    re_path(r"^matcher/update/", apply_match, name="apply_person_match",),
]
