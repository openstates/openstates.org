import pytest
from graphapi.tests.utils import populate_db
from opencivicdata.core.models import Person


@pytest.mark.django_db
def setup():
    populate_db()


BILLS_QUERY_COUNT = 10
ALASKA_BILLS = 12


@pytest.mark.django_db
def test_bills_view_basics(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        resp = client.get("/public/ak/bills")
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "bills"
    assert len(resp.context["chambers"]) == 2
    assert len(resp.context["sessions"]) == 2
    assert "nature" in resp.context["subjects"]
    assert len(resp.context["sponsors"]) == 6
    assert len(resp.context["classifications"]) == 3
    # 10 random bills, 2 full featured
    assert len(resp.context["bills"]) == ALASKA_BILLS


@pytest.mark.django_db
def test_bills_view_query(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        resp = client.get("/public/ak/bills?query=Moose")
    assert resp.status_code == 200
    assert len(resp.context["bills"]) == 1

    # test that a query doesn't alter the search options
    assert len(resp.context["chambers"]) == 2
    assert len(resp.context["sessions"]) == 2
    assert "nature" in resp.context["subjects"]
    assert len(resp.context["subjects"]) > 10
    assert len(resp.context["sponsors"]) == 6
    assert len(resp.context["classifications"]) == 3


@pytest.mark.django_db
def test_bills_view_chamber(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        upper = len(client.get("/public/ak/bills?chamber=upper").context["bills"])
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        lower = len(client.get("/public/ak/bills?chamber=lower").context["bills"])
    assert upper + lower == ALASKA_BILLS


@pytest.mark.django_db
def test_bills_view_session(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        b17 = len(client.get("/public/ak/bills?session=2017").context["bills"])
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        b18 = len(client.get("/public/ak/bills?session=2018").context["bills"])
    assert b17 + b18 == ALASKA_BILLS


@pytest.mark.django_db
def test_bills_view_sponsor(client, django_assert_num_queries):
    amanda = Person.objects.get(name="Amanda Adams")
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        assert (
            len(client.get(f"/public/ak/bills?sponsor={amanda.id}").context["bills"])
            == 1
        )


@pytest.mark.django_db
def test_bills_view_classification(client, django_assert_num_queries):
    bills = len(client.get("/public/ak/bills?classification=bill").context["bills"])
    resolutions = len(
        client.get("/public/ak/bills?classification=resolution").context["bills"]
    )
    assert (
        len(
            client.get(
                "/public/ak/bills?classification=constitutional+amendment"
            ).context["bills"]
        )
        == 2
    )
    assert bills + resolutions == ALASKA_BILLS


@pytest.mark.django_db
def test_bills_view_subject(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        assert (
            len(client.get(f"/public/ak/bills?subjects=nature").context["bills"]) == 2
        )


@pytest.mark.django_db
def test_bills_view_status(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        assert (
            len(
                client.get(f"/public/ak/bills?status=passed-lower-chamber").context[
                    "bills"
                ]
            )
            == 1
        )


@pytest.mark.django_db
def test_bill_view(client, django_assert_num_queries):
    with django_assert_num_queries(11):
        resp = client.get("/public/ak/bills/2018/HB1")
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "bills"
    assert resp.context["bill"].identifier == "HB 1"
    assert len(resp.context["sponsorships"]) == 2
    assert len(resp.context["actions"]) == 3
    assert len(resp.context["votes"]) == 1
    assert len(resp.context["versions"]) == 2
    assert len(resp.context["documents"]) == 2
    assert resp.context["read_link"] == "https://example.com/f.txt"
