import pytest
from graphapi.tests.utils import populate_db
from public.models import PersonProxy


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_legislators_view(client, django_assert_num_queries):
    with django_assert_num_queries(5):
        resp = client.get("/ak/legislators/")
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "legislators"
    assert len(resp.context["chambers"]) == 2
    assert len(resp.context["legislators"]) == 6


@pytest.mark.django_db
def test_person_view(client, django_assert_num_queries):
    p = PersonProxy.objects.get(name="Amanda Adams")
    with django_assert_num_queries(10):
        resp = client.get(p.pretty_url())
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "legislators"
    person = resp.context["person"]
    assert person.name == "Amanda Adams"
    assert person.current_role == {
        "chamber": "lower",
        "district": 1,
        "division_id": "ocd-division/country:us/state:Alaska/district:1",
        "state": "ak",
        "role": "",
        "party": "Republican",
    }
    assert len(person.sponsored_bills) == 1
    assert len(person.vote_events) == 1
    assert resp.context["retired"] is False


@pytest.mark.django_db
def test_person_view_retired(client, django_assert_num_queries):
    p = PersonProxy.objects.get(name="Rhonda Retired")
    # fewer views, we don't do the bill queries
    with django_assert_num_queries(9):
        resp = client.get(p.pretty_url())
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "legislators"
    person = resp.context["person"]
    assert person.name == "Rhonda Retired"
    assert resp.context["retired"] is True


@pytest.mark.django_db
def test_canonicalize_person(client):
    p = PersonProxy.objects.get(name="Amanda Adams")
    url = p.pretty_url().replace("amanda", "xyz")
    assert "xyz" in url
    resp = client.get(url)
    assert resp.status_code == 301
    assert resp.url == p.pretty_url()


# TODO: test find_your_legislator
