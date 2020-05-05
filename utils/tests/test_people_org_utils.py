import pytest
from graphapi.tests.utils import populate_db
from utils.orgs import get_chambers_from_abbr, get_legislature_from_abbr


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
