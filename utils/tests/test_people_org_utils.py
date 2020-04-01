import pytest
from graphapi.tests.utils import populate_db
from utils.orgs import get_chambers_from_abbr, get_legislature_from_abbr
from utils.people import get_current_role
from openstates_core.data.models import Person


@pytest.mark.django_db
def test_get_chambers():
    populate_db()
    chambers = get_chambers_from_abbr("ak")
    assert len(chambers) == 2
    assert {"upper", "lower"} == {c.classification for c in chambers}


@pytest.mark.django_db
def test_get_legislature():
    populate_db()
    assert get_legislature_from_abbr("ak").name == "Alaska Legislature"


@pytest.mark.django_db
def test_get_current_role():
    populate_db()
    p = Person.objects.get(name="Amanda Adams")
    role = get_current_role(p)
    assert role == {
        "party": "Republican",
        "chamber": "lower",
        "district": "1",
        "division_id": "ocd-division/country:us/state:Alaska/district:1",
        "role": "",
        "state": "ak",
    }
