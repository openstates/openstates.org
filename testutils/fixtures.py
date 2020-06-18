import pytest
from openstates.data.models import (
    Division,
    Jurisdiction,
    Organization,
)


@pytest.fixture
def kansas():
    d = Division.objects.create(id="ocd-division/country:us/state:ks", name="Kansas")
    j = Jurisdiction.objects.create(
        id="ocd-jurisdiction/country:us/state:ks/government", name="Kansas", division=d
    )
    j.legislative_sessions.create(
        identifier="2019", name="2019", start_date="2019-01-01"
    )
    j.legislative_sessions.create(
        identifier="2020", name="2020", start_date="2020-01-01"
    )

    leg = Organization.objects.create(
        jurisdiction=j, classification="legislature", name="Kansas Legislature"
    )
    Organization.objects.create(
        jurisdiction=j, parent=leg, classification="lower", name="Kansas House"
    )
    Organization.objects.create(
        jurisdiction=j, parent=leg, classification="upper", name="Kansas Senate"
    )
    return j
