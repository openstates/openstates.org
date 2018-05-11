from django.urls import path, re_path

from .views.other import styleguide, home, state
from .views.legislators import legislators, legislator
from .views.bills import bills, bill
from .views.committees import committees, committee
from .utils import states


OCD_ID_PATTERN = r'[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}'
# Only allow valid state abbreviations
state_abbrs = [s.abbr.lower() for s in states]
state_abbr_pattern = r'({})'.format('|'.join(state_abbrs))

urlpatterns = [
    path('styleguide', styleguide, name='styleguide'),

    path('', home, name='home'),

    re_path(r'^(?P<state>{})$'.format(state_abbr_pattern), state, name='state'),

    re_path(r'^(?P<state>{})/legislators$'.format(state_abbr_pattern), legislators,
            name='legislators'),
    re_path(r'^(?P<state>{})/legislators/(?P<legislator_id>ocd-person/{})$'.format(
        state_abbr_pattern, OCD_ID_PATTERN), legislator, name='legislator'),

    re_path(r'^(?P<state>{})/bills$'.format(state_abbr_pattern),
            bills, name='bills'),
    re_path(r'^(?P<state>{})/bills/(?P<bill_id>ocd-bill/{})$'.format(
        state_abbr_pattern, OCD_ID_PATTERN), bill, name='bill'),

    re_path(r'^(?P<state>{})/committees$'.format(state_abbr_pattern), committees,
            name='committees'),
    re_path(r'^(?P<state>{})/committees/(?P<bill_id>ocd-organization/{})$'.format(
        state_abbr_pattern, OCD_ID_PATTERN), committee, name='committee'),
]
