from django.urls import path, re_path
import us

from . import views


OCD_ID_PATTERN = r'[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}'
# Only allow valid state abbreviations
all_state_abbrs = [s.abbr.lower() for s in us.STATES_AND_TERRITORIES]
state_abbr_pattern = r'({})'.format('|'.join(all_state_abbrs))

urlpatterns = [
    path('styleguide', views.styleguide, name='styleguide'),

    re_path(r'^(?P<state>{})$'.format(state_abbr_pattern), views.jurisdiction, name='jurisdiction'),

    re_path(r'^(?P<state>{})/legislators$'.format(state_abbr_pattern), views.legislators, name='legislators'),
    re_path(r'^(?P<state>{})/legislators/(?P<legislator_id>ocd-person/{})$'.format(state_abbr_pattern, OCD_ID_PATTERN), views.legislator, name='legislator'),

    re_path(r'^(?P<state>{})/bills$'.format(state_abbr_pattern), views.bills, name='bills'),
    re_path(r'^(?P<state>{})/bills/(?P<bill_id>ocd-bill/{})$'.format(state_abbr_pattern, OCD_ID_PATTERN), views.bill, name='bill'),

    re_path(r'^(?P<state>{})/committees$'.format(state_abbr_pattern), views.committees, name='committees'),
    re_path(r'^(?P<state>{})/committees/(?P<bill_id>ocd-organization/{})$'.format(state_abbr_pattern, OCD_ID_PATTERN), views.committee, name='committee'),
]
