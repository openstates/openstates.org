import pytest
from utils.cli import yield_state_sessions
from openstates.data.models import Division, Jurisdiction, Bill


@pytest.fixture
def sessions():
    for state in ("ks", "wy"):
        d = Division.objects.create(
            id=f"ocd-division/country:us/state:{state}", name=state
        )
        j = Jurisdiction.objects.create(
            id=f"ocd-jurisdiction/country:us/state:{state}/government",
            name=state,
            division=d,
        )
        ls = j.legislative_sessions.create(
            identifier="2019", name="2019", start_date="2019-01-01"
        )
        Bill.objects.create(identifier="HB1", legislative_session=ls)
        ls = j.legislative_sessions.create(
            identifier="2020", name="2020", start_date="2020-01-01"
        )
        Bill.objects.create(identifier="HB1", legislative_session=ls)


def test_yield_state_sessions_simplest():
    results = list(yield_state_sessions("ks", "2020"))
    assert results == [("ks", "2020")]


@pytest.mark.django_db
def test_yield_state_sessions_one_state(sessions):
    results = list(yield_state_sessions("ks", None))
    assert results == [("ks", "2019"), ("ks", "2020")]


@pytest.mark.django_db
def test_yield_state_sessions_all_state(sessions):
    # just the latest session for each state
    results = list(yield_state_sessions("all", None))
    assert results == [("ks", "2020"), ("wy", "2020")]


@pytest.mark.django_db
def test_yield_state_sessions_all_sessions(sessions):
    # just the latest session for each state
    results = list(yield_state_sessions("all_sessions", None))
    assert results == [("ks", "2019"), ("ks", "2020"), ("wy", "2019"), ("wy", "2020")]
