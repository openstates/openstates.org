import pytest
from graphapi.tests.utils import populate_db
from openstates_core.data.models import Organization, Person, Membership
from utils.common import pretty_url


@pytest.mark.django_db
def setup():
    populate_db()
    house = Organization.objects.get(
        classification="lower", jurisdiction__name="Alaska"
    )
    r = Organization.objects.create(
        name="Robots",
        classification="committee",
        parent=house,
        jurisdiction=house.jurisdiction,
    )
    w = Organization.objects.create(
        name="Wizards",
        classification="committee",
        parent=house,
        jurisdiction=house.jurisdiction,
    )
    # one robot
    p = Person.objects.get(name="Amanda Adams")
    Membership.objects.create(person=p, organization=r)
    # all are wizards
    for p in Person.objects.all()[:5]:
        Membership.objects.create(person=p, organization=w)


@pytest.mark.django_db
def test_committees_view(client, django_assert_num_queries):
    with django_assert_num_queries(3):
        resp = client.get("/ak/committees/")
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "committees"
    assert len(resp.context["chambers"]) == 2
    assert len(resp.context["committees"]) == 2

    # check member_counts
    one, two = resp.context["committees"]
    if one["name"] == "Robots":
        robots, wizards = one, two
    else:
        robots, wizards = two, one
    assert robots["member_count"] == 1
    assert wizards["member_count"] == 5


@pytest.mark.django_db
def test_committee_detail(client, django_assert_num_queries):
    o = Organization.objects.get(name="Wizards")
    with django_assert_num_queries(9):
        resp = client.get(pretty_url(o))
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "committees"
    org = resp.context["committee"]
    assert org.name == "Wizards"
    assert len(resp.context["memberships"]) == 5


@pytest.mark.django_db
def test_canonicalize_committee(client):
    o = Organization.objects.get(name="Wizards")
    url = pretty_url(o).replace("wizards", "xyz")
    assert "xyz" in url
    resp = client.get(url)
    assert resp.status_code == 301
    assert resp.url == pretty_url(o)
