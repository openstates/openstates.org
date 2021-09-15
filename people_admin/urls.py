from django.urls import path, re_path
from utils.common import states
from .views import (
    jurisdiction_list,
    people_list,
    people_matcher,
    apply_match,
    apply_retirement,
    new_legislator,
    apply_new_legislator,
    apply_bulk_edits,
    create_delta_sets,
    create_pr,
)

# Only allow valid state abbreviations
state_abbrs = [s.abbr.lower() for s in states] + ["us"]
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
    re_path(
        r"^matcher/update/",
        apply_match,
        name="apply_person_match",
    ),
    re_path(
        r"^retire/",
        apply_retirement,
        name="apply_retirement",
    ),
    re_path(
        r"^(?P<state>{})/new_legislator/$".format(state_abbr_pattern),
        new_legislator,
        name="new_legislator",
    ),
    re_path(
        r"^new_legislator/",
        apply_new_legislator,
        name="apply_new_legislator",
    ),
    re_path(
        r"^bulk/",
        apply_bulk_edits,
        name="apply_bulk_edits",
    ),
    re_path(
        r"^(?P<state>{})/deltas/$".format(state_abbr_pattern),
        create_delta_sets,
        name="create_delta_sets",
    ),
    re_path(
        r"^create_pr/",
        create_pr,
        name="create_pr",
    ),
]
