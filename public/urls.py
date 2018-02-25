from django.urls import re_path
import us

from . import views


OCD_ID_PATTERN = r'[a-z\d]{8}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{4}-[a-z\d]{12}'
# Only allow valid state abbreviations
all_state_abbrs = [s.abbr.lower() for s in us.STATES_AND_TERRITORIES]
state_abbr_pattern = r'({})'.format('|'.join(all_state_abbrs))

urlpatterns = [
    re_path(r'^styleguide$', views.styleguide, name='styleguide'),
    re_path(r'^(?P<state>{})/legislators$', views.legislators, name='legislators'),
    re_path(r'^(?P<state>{})/legislators/(?P<legislator_id>ocd-person/{})$'.format(state_abbr_pattern, OCD_ID_PATTERN), views.legislator, name='legislator'),
]
