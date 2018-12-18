from django.urls import path, re_path
from django.views.generic import TemplateView
from .views.other import styleguide, home, state
from .views.legislators import legislators, person, find_your_legislator
from .views.bills import BillList, BillListFeed, bill, vote
from .views.committees import committees, committee
from .views.donations import donate
from .views.fallback import fallback
from utils.common import states


OCD_ID_PATTERN = r"[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}"
# Only allow valid state abbreviations
state_abbrs = [s.abbr.lower() for s in states]
state_abbr_pattern = r"({})".format("|".join(state_abbrs))

urlpatterns = [
    path("styleguide", styleguide, name="styleguide"),

    # flatpages
    path('about/', TemplateView.as_view(template_name='flat/about.html')),
    path('tos/', TemplateView.as_view(template_name='flat/tos.html')),
    path('donate/', donate),

    # top level views
    path("", home, name="home"),
    path("find_your_legislator/", find_your_legislator, name="find_your_legislator"),
    re_path(r"^(?P<state>{})/$".format(state_abbr_pattern), state, name="state"),
    # people
    re_path(
        r"^(?P<state>{})/legislators/$".format(state_abbr_pattern),
        legislators,
        name="legislators",
    ),
    re_path(r"^person/.*\-(?P<person_id>[0-9A-Za-z]+)/$", person, name="person-detail"),
    # bills
    re_path(
        r"^(?P<state>{})/bills/$".format(state_abbr_pattern),
        BillList.as_view(),
        name="bills",
    ),
    # has trailing slash for consistency
    re_path(
        r"^(?P<state>{})/bills/feed/$".format(state_abbr_pattern),
        BillListFeed.as_view(),
        name="bills_feed",
    ),
    re_path(
        r"^(?P<state>{})/bills/(?P<session>\w+)/(?P<bill_id>\w+)/$".format(
            state_abbr_pattern
        ),
        bill,
        name="bill",
    ),
    re_path(r"^vote/(?P<vote_id>[-0-9a-f]+)/$", vote, name="vote-detail"),
    # committees
    re_path(
        r"^(?P<state>{})/committees/$".format(state_abbr_pattern),
        committees,
        name="committees",
    ),
    re_path(
        r"^(?P<state>{})/committees/.*\-(?P<committee_id>[0-9A-Za-z]+)/$".format(
            state_abbr_pattern
        ),
        committee,
        name="committee-detail",
    ),

    # fallbacks
    path('reportcard/', fallback),
    # re_path(r'[a-z]{2}/bills/', fallback),
]
