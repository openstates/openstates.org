import pytest
from graphapi.tests.utils import populate_db
from openstates.data.models import Person, VoteEvent
from testutils.factories import create_test_bill


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.fixture
def sortable_bills(kansas):
    # A's introduced first
    # B's latest action is first
    # C's introduced last
    b = create_test_bill("2020", "upper", identifier="A")
    b.first_action_date = "2020-01-01"
    b.latest_action_date = "2020-08-01"
    b.save()
    b = create_test_bill("2020", "upper", identifier="B")
    b.first_action_date = "2020-01-02"
    b.latest_action_date = "2020-06-01"
    b.save()
    b = create_test_bill("2020", "upper", identifier="C")
    b.first_action_date = "2020-07-01"
    b.latest_action_date = "2020-07-01"
    b.save()


BILLS_QUERY_COUNT = 7
ALASKA_BILLS = 12


@pytest.mark.django_db
def test_bills_view_basics(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        resp = client.get("/ak/bills/")
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "bills"
    assert len(resp.context["chambers"]) == 2
    assert len(resp.context["sessions"]) == 2
    assert "nature" in resp.context["subjects"]
    assert len(resp.context["sponsors"]) == 7
    assert len(resp.context["classifications"]) == 3
    # 10 random bills, 2 full featured
    assert len(resp.context["bills"]) == ALASKA_BILLS


@pytest.mark.django_db
def test_bills_view_query(client, django_assert_num_queries):
    # title search works
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        resp = client.get("/ak/bills/?query=moose")
    assert resp.status_code == 200
    assert len(resp.context["bills"]) == 1

    # search in body works
    resp = client.get("/ak/bills/?query=gorgonzola")
    assert resp.status_code == 200
    assert len(resp.context["bills"]) == 1

    # test that a query doesn't alter the search options
    assert len(resp.context["chambers"]) == 2
    assert len(resp.context["sessions"]) == 2
    assert "nature" in resp.context["subjects"]
    assert len(resp.context["subjects"]) > 10
    assert len(resp.context["sponsors"]) == 7
    assert len(resp.context["classifications"]) == 3


@pytest.mark.django_db
def test_bills_view_query_bill_id(client, django_assert_num_queries):
    # query by bill id
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        resp = client.get("/ak/bills/?query=HB 1")
    assert resp.status_code == 200
    assert len(resp.context["bills"]) == 1

    # case insensitive
    resp = client.get("/ak/bills/?query=hb 1")
    assert resp.status_code == 200
    assert len(resp.context["bills"]) == 1


@pytest.mark.django_db
def test_bills_view_chamber(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        upper = len(client.get("/ak/bills/?chamber=upper").context["bills"])
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        lower = len(client.get("/ak/bills/?chamber=lower").context["bills"])
    assert upper + lower == ALASKA_BILLS


@pytest.mark.django_db
def test_bills_view_session(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        b17 = len(client.get("/ak/bills/?session=2017").context["bills"])
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        b18 = len(client.get("/ak/bills/?session=2018").context["bills"])
    assert b17 + b18 == ALASKA_BILLS


@pytest.mark.django_db
def test_bills_view_sponsor(client, django_assert_num_queries):
    amanda = Person.objects.get(name="Amanda Adams")
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        assert len(client.get(f"/ak/bills/?sponsor={amanda.id}").context["bills"]) == 2


@pytest.mark.django_db
def test_bills_view_classification(client, django_assert_num_queries):
    bills = len(client.get("/ak/bills/?classification=bill").context["bills"])
    resolutions = len(
        client.get("/ak/bills/?classification=resolution").context["bills"]
    )
    assert (
        len(
            client.get("/ak/bills/?classification=constitutional+amendment").context[
                "bills"
            ]
        )
        == 2
    )
    assert bills + resolutions == ALASKA_BILLS


@pytest.mark.django_db
def test_bills_view_subject(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        assert len(client.get("/ak/bills/?subjects=nature").context["bills"]) == 2


@pytest.mark.django_db
def test_bills_view_status(client, django_assert_num_queries):
    with django_assert_num_queries(BILLS_QUERY_COUNT):
        assert (
            len(client.get("/ak/bills/?status=passed-lower-chamber").context["bills"])
            == 1
        )


@pytest.mark.django_db
def test_bills_view_sort_latest_action(
    client, django_assert_num_queries, sortable_bills
):
    bills = client.get("/ks/bills/?sort=latest_action").context["bills"]
    assert len(bills) == 3
    assert bills[0].identifier == "B"
    assert bills[1].identifier == "C"
    assert bills[2].identifier == "A"
    assert (
        bills[0].last_action_date
        < bills[1].last_action_date
        < bills[2].last_action_date
    )

    # reverse
    bills = client.get("/ks/bills/?sort=-latest_action").context["bills"]
    assert bills[0].identifier == "A"
    assert bills[1].identifier == "C"
    assert bills[2].identifier == "B"

    # no sort provided, same as -latest_action
    bills = client.get("/ks/bills/?").context["bills"]
    assert bills[0].identifier == "A"
    assert bills[1].identifier == "C"
    assert bills[2].identifier == "B"


@pytest.mark.django_db
def test_bills_view_sort_first_action(
    client, django_assert_num_queries, sortable_bills
):
    bills = client.get("/ks/bills/?sort=first_action").context["bills"]
    for b in bills:
        print(b.identifier, b.first_action_date)
    assert len(bills) == 3
    assert bills[0].identifier == "A"
    assert bills[1].identifier == "B"
    assert bills[2].identifier == "C"
    assert (
        bills[0].first_action_date
        < bills[1].first_action_date
        < bills[2].first_action_date
    )

    # reverse
    bills = client.get("/ks/bills/?sort=-first_action").context["bills"]
    assert bills[0].identifier == "C"
    assert bills[1].identifier == "B"
    assert bills[2].identifier == "A"


@pytest.mark.django_db
def test_bills_view_bad_page(client):
    resp = client.get("/ak/bills/?page=A")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_bill_view(client, django_assert_num_queries):
    with django_assert_num_queries(17):
        resp = client.get("/ak/bills/2018/HB1/")
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "bills"
    assert resp.context["bill"].identifier == "HB 1"
    assert len(resp.context["sponsorships"]) == 2
    assert len(resp.context["actions"]) == 3
    assert resp.context["actions"][0].date > resp.context["actions"][2].date
    assert len(resp.context["votes"]) == 1
    assert len(resp.context["versions"]) == 2
    assert len(resp.context["documents"]) == 2
    assert resp.context["read_link"] == "https://example.com/f.pdf"
    assert resp.context["stages"][1] == {
        "date": "2018-03-01",
        "stage": "Alaska House",
        "text": "Passed Alaska House",
    }


@pytest.mark.django_db
def test_vote_view(client, django_assert_num_queries):
    vid = VoteEvent.objects.get(motion_text="Vote on House Passage").id.split("/")[1]
    with django_assert_num_queries(7):
        resp = client.get(f"/vote/{vid}/")
    assert resp.status_code == 200
    assert resp.context["state"] == "ak"
    assert resp.context["state_nav"] == "bills"
    assert len(resp.context["person_votes"]) == 5

    # vote counts in order, yes, no, others
    assert resp.context["vote_counts"][0].option == "yes"
    assert resp.context["vote_counts"][1].option == "no"
    assert resp.context["vote_counts"][0].value == 1
    assert resp.context["vote_counts"][1].value == 4

    # sorted list of (party, counts) pairs
    assert resp.context["party_votes"][0][0] == "Democratic"
    assert resp.context["party_votes"][0][1]["no"] == 1
    assert resp.context["party_votes"][0][1]["yes"] == 0
    assert resp.context["party_votes"][1][0] == "Republican"
    assert resp.context["party_votes"][1][1]["no"] == 2
    assert resp.context["party_votes"][1][1]["yes"] == 1
    assert resp.context["party_votes"][2][0] == "Unknown"
    assert resp.context["party_votes"][2][1]["no"] == 1


@pytest.mark.django_db
def test_bills_feed(client):
    resp = client.get("/ak/bills/feed/")
    assert resp.status_code == 200
