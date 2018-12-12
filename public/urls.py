from django.urls import path, re_path

from .views.other import styleguide, home, state, unslash
from .views.legislators import legislators, person, find_your_legislator
from .views.bills import bills, bill
from .views.committees import committees, committee
from utils.common import states


OCD_ID_PATTERN = r"[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}"
# Only allow valid state abbreviations
state_abbrs = [s.abbr.lower() for s in states]
state_abbr_pattern = r"({})".format("|".join(state_abbrs))

urlpatterns = [
    path("styleguide", styleguide, name="styleguide"),
    # top level views
    path("", home, name="home"),
    path("find_your_legislator", find_your_legislator, name="find_your_legislator"),
    re_path(r"^(?P<state>{})$".format(state_abbr_pattern), state, name="state"),
    # people
    re_path(
        r"^(?P<state>{})/legislators$".format(state_abbr_pattern),
        legislators,
        name="legislators",
    ),
    re_path(r"^person/.*\-(?P<person_id>[0-9A-Za-z]+)", person, name="person-detail"),
    re_path(r"^(?P<state>{})/bills$".format(state_abbr_pattern), bills, name="bills"),
    re_path(
        r"^(?P<state>{})/bills/(?P<session>\w+)/(?P<bill_id>\w+)$".format(
            state_abbr_pattern
        ),
        bill,
        name="bill",
    ),
    re_path(
        r"^(?P<state>{})/committees$".format(state_abbr_pattern),
        committees,
        name="committees",
    ),
    re_path(
        r"^(?P<state>{})/committees/(?P<bill_id>ocd-organization/{})$".format(
            state_abbr_pattern, OCD_ID_PATTERN
        ),
        committee,
        name="committee",
    ),
    # TODO: before release we need to make this sane and choose a side
    # redirect some old slashed URLs
    path("find_your_legislator/", unslash),
    re_path(r"^(?P<state>{})/$".format(state_abbr_pattern), unslash),
    re_path(r"^(?P<state>{})/legislators/$".format(state_abbr_pattern), unslash),
    re_path(r"^(?P<state>{})/bills/$".format(state_abbr_pattern), unslash),
    re_path(r"^(?P<state>{})/committees/$".format(state_abbr_pattern), unslash),
]
