import pytest
from django.contrib.auth.models import User
from graphapi.tests.utils import populate_db
from openstates.data.models import Person, Bill
from ..models import LegacyBillMapping


@pytest.mark.django_db
def setup():
    populate_db()
    # add legacy ID to bill
    LegacyBillMapping.objects.create(
        legacy_id="AKB00000001", bill=Bill.objects.get(identifier="HB 1")
    )
    u = User.objects.create(username="testkey")
    u.profile.api_key = "testkey"
    u.profile.api_tier = "unlimited"
    u.profile.save()


HEADERS = {"HTTP_X_API_KEY": "testkey"}


@pytest.mark.django_db
def test_no_api_key(client, django_assert_num_queries):
    with django_assert_num_queries(0):
        resp = client.get("/api/v1/metadata/ak/")
        assert resp.status_code == 403
        assert resp.json()["error"] == "must provide an API key"


@pytest.mark.django_db
def test_metadata_detail(client, django_assert_num_queries):
    with django_assert_num_queries(5):
        resp = client.get("/api/v1/metadata/ak/", **HEADERS)
        assert resp.status_code == 200
        assert resp.json() == {
            "id": "ak",
            "name": "Alaska",
            "abbreviation": "ak",
            "legislature_name": "Alaska Legislature",
            "legislature_url": "",
            "chambers": {
                "upper": {"name": "Alaska Senate", "title": "Senator"},
                "lower": {"name": "Alaska House", "title": "Representative"},
            },
            "session_details": {
                "2018": {
                    "display_name": "2018",
                    "type": "",
                    "start_date": "2018-01-01 00:00:00",
                },
                "2017": {
                    "display_name": "2017",
                    "type": "",
                    "start_date": "2017-01-01 00:00:00",
                },
            },
            "latest_update": "2000-01-01 00:00:00",
            "capitol_timezone": "America/Anchorage",
            "terms": [
                {
                    "end_year": 2012,
                    "name": "27",
                    "sessions": ["27"],
                    "start_year": 2011,
                },
                {
                    "end_year": 2014,
                    "name": "28",
                    "sessions": ["28"],
                    "start_year": 2013,
                },
                {
                    "end_year": 2016,
                    "name": "29",
                    "sessions": ["29"],
                    "start_year": 2015,
                },
                {
                    "end_year": 2018,
                    "name": "30",
                    "sessions": ["30"],
                    "start_year": 2017,
                },
            ],
            "feature_flags": [],
            "latest_csv_date": "2018-11-03 00:00:00",
            "latest_csv_url": "https://data.openstates.org/legacy/csv/ak.zip",
            "latest_json_date": "2018-11-03 00:00:00",
            "latest_json_url": "https://data.openstates.org/legacy/json/ak.zip",
        }


@pytest.mark.django_db
def test_metadata_list(client, django_assert_num_queries):
    with django_assert_num_queries(5):
        resp = client.get("/api/v1/metadata/", **HEADERS)
        assert resp.status_code == 200


@pytest.mark.django_db
def test_bill_detail(client, django_assert_num_queries):
    with django_assert_num_queries(20):
        resp = client.get("/api/v1/bills/ak/2018/HB 1/", **HEADERS)
        assert resp.status_code == 200
        bill = resp.json()
        bill.pop("created_at")
        bill.pop("updated_at")
        assert bill["title"] == "Moose Freedom Act"
        assert bill["summary"] == "Grants all moose equal rights under the law."
        assert bill["id"] == "AKB00000001"
        assert bill["chamber"] == "lower"
        assert bill["state"] == "ak"
        assert bill["session"] == "2018"
        assert bill["type"] == ["bill", "constitutional amendment"]
        assert bill["bill_id"] == "HB 1"
        assert bill["actions"] == [
            {
                "date": "2018-01-01 00:00:00",
                "action": "Introduced",
                "type": [],
                "related_entities": [],
                "actor": "lower",
            },
            {
                "date": "2018-02-01 00:00:00",
                "action": "Amended",
                "type": [],
                "related_entities": [],
                "actor": "lower",
            },
            {
                "date": "2018-03-01 00:00:00",
                "action": "Passed House",
                "type": ["bill:passed"],
                "related_entities": [],
                "actor": "lower",
            },
        ]
        assert len(bill["sources"]) == 3
        assert len(bill["sponsors"]) == 2
        assert len(bill["versions"]) == 4
        assert len(bill["documents"]) == 2
        assert len(bill["alternate_titles"]) == 3
        assert len(bill["votes"]) == 1
        assert bill["votes"][0]["session"] == "2018"
        assert bill["votes"][0]["yes_count"] == 1
        assert bill["votes"][0]["no_count"] == 4
        assert len(bill["votes"][0]["yes_votes"]) == 1
        assert len(bill["votes"][0]["no_votes"]) == 4
        assert bill["action_dates"] == {
            "first": "2018-01-01 00:00:00",
            "last": "2018-03-01 00:00:00",
            "passed_upper": None,
            "passed_lower": None,
            "signed": None,
        }
        assert bill["scraped_subjects"] == ["nature"]


@pytest.mark.django_db
def test_bill_detail_alternate_forms(client):
    resp = client.get("/api/v1/bills/ak/2018/HB 1/", **HEADERS).json()
    assert client.get("/api/v1/bills/ak/2018/lower/HB 1/", **HEADERS).json() == resp
    assert client.get("/api/v1/bills/AKB00000001/", **HEADERS).json() == resp


@pytest.mark.django_db
def test_bill_list_basic(client, django_assert_num_queries):
    with django_assert_num_queries(14):
        # need updated_since on there to avoid too-big detection
        resp = client.get("/api/v1/bills/?updated_since=2017-01-01", **HEADERS)
        assert len(resp.json()) == 26
        assert resp.status_code == 200


@pytest.mark.django_db
def test_bill_list_state_param(client):
    wy = client.get("/api/v1/bills/?state=wy&updated_since=2017-01-01", **HEADERS)
    ak = client.get("/api/v1/bills/?state=ak&updated_since=2017-01-01", **HEADERS)
    assert len(wy.json()) + len(ak.json()) == 26


@pytest.mark.django_db
def test_bill_list_chamber_param(client):
    wy = client.get("/api/v1/bills/?state=wy&updated_since=2017-01-01", **HEADERS)
    upper = client.get(
        "/api/v1/bills/?state=wy&chamber=upper&updated_since=2017-01-01", **HEADERS
    )
    lower = client.get(
        "/api/v1/bills/?state=wy&chamber=lower&updated_since=2017-01-01", **HEADERS
    )
    assert len(upper.json()) + len(lower.json()) == len(wy.json())


@pytest.mark.django_db
def test_bill_list_bill_id_param(client):
    hb1 = client.get("/api/v1/bills/?bill_id=HB 1", **HEADERS)
    assert len(hb1.json()) == 1


@pytest.mark.django_db
def test_bill_list_q_param(client):
    moose = client.get("/api/v1/bills/?q=moose", **HEADERS)
    assert len(moose.json()) == 1
    assert moose.json()[0]["title"] == "Moose Freedom Act"


@pytest.mark.django_db
def test_bill_list_search_window_param(client):
    wy = client.get("/api/v1/bills/?state=wy&updated_since=2017-01-01", **HEADERS)
    session2017 = client.get(
        "/api/v1/bills/?state=wy&search_window=session:2017", **HEADERS
    )
    session2018 = client.get(
        "/api/v1/bills/?state=wy&search_window=session:2018", **HEADERS
    )
    session_now = client.get("/api/v1/bills/?state=wy&search_window=session", **HEADERS)
    assert len(session2017.json()) + len(session2018.json()) == len(wy.json())
    assert session2018.json() == session_now.json()


@pytest.mark.django_db
def test_bill_list_updated_since_param(client):
    since = client.get("/api/v1/bills/?updated_since=2018-01-01", **HEADERS)
    assert len(since.json()) == 26
    since = client.get("/api/v1/bills/?updated_since=2038-01-01", **HEADERS)
    assert len(since.json()) == 0


@pytest.mark.django_db
def test_bill_list_sort(client):
    all = client.get(
        "/api/v1/bills/?sort=created_at&updated_since=2017-01-01", **HEADERS
    ).json()
    assert all[0]["created_at"] >= all[10]["created_at"] >= all[-1]["created_at"]

    some_bill = Bill.objects.all()[16]
    some_bill.title = "latest updated"
    some_bill.save()
    all = client.get(
        "/api/v1/bills/?sort=updated_at&updated_since=2017-01-01", **HEADERS
    ).json()
    assert all[0]["updated_at"] >= all[10]["updated_at"] >= all[-1]["updated_at"]
    assert all[0]["title"] == "latest updated"


@pytest.mark.django_db
def test_legislator_detail(client, django_assert_num_queries):
    leg = Person.objects.get(name="Amanda Adams")
    leg.identifiers.create(scheme="legacy_openstates", identifier="AKL000001")

    with django_assert_num_queries(9):
        resp = client.get("/api/v1/legislators/AKL000001/", **HEADERS)
        assert resp.status_code == 200
        resp = resp.json()
        resp.pop("updated_at")
        resp.pop("created_at")
        amanda = {
            "id": "AKL000001",
            "leg_id": "AKL000001",
            "all_ids": ["AKL000001"],
            "full_name": "Amanda Adams",
            "first_name": "",
            "last_name": "Amanda Adams",
            "suffix": "",
            "photo_url": "",
            "url": "",
            "email": None,
            "party": "Republican",
            "chamber": "lower",
            "district": 1,
            "state": "ak",
            "sources": [],
            "active": True,
            "roles": [
                {
                    "term": "30",
                    "district": 1,
                    "chamber": "lower",
                    "state": "ak",
                    "party": "Republican",
                    "type": "member",
                    "start_date": None,
                    "end_date": None,
                }
            ],
            "offices": [],
            "old_roles": {},
            "middle_name": "",
            "country": "us",
            "level": "state",
        }
        assert amanda == resp


@pytest.mark.django_db
def test_legislator_list_basic(client, django_assert_num_queries):
    with django_assert_num_queries(9):
        resp = client.get("/api/v1/legislators/", **HEADERS)
        assert resp.status_code == 200


@pytest.mark.django_db
def test_legislator_list_params(client, django_assert_num_queries):
    # check state filter
    resp = client.get("/api/v1/legislators/", **HEADERS)
    assert len(resp.json()) == 8
    resp = client.get("/api/v1/legislators/?state=wy", **HEADERS)
    assert len(resp.json()) == 2

    # check chamber filter
    resp = client.get("/api/v1/legislators/?state=ak&chamber=upper", **HEADERS)
    assert len(resp.json()) == 2
    resp = client.get("/api/v1/legislators/?state=ak&chamber=lower", **HEADERS)
    assert len(resp.json()) == 4

    # district filter
    resp = client.get("/api/v1/legislators/?district=1", **HEADERS)
    assert len(resp.json()) == 3


# @pytest.mark.django_db
# def test_legislator_geo(client, django_assert_num_queries):
#     pass


@pytest.mark.django_db
def test_districts_list(client, django_assert_num_queries):
    with django_assert_num_queries(2):
        resp = client.get("/api/v1/districts/ak/", **HEADERS)
        assert resp.status_code == 200
        assert len(resp.json()) == 8
        expected = {
            "division_id": "ocd-division/country:us/state:ak/sldu:b",
            "boundary_id": "ocd-division/country:us/state:ak/sldu:b",
            "name": "B",
            "chamber": "upper",
            "abbr": "ak",
            "legislators": [],
            "num_seats": 1,
            "id": "ak-upper-B",
        }
        assert expected in resp.json()

    # test filtering by URL
    resp = client.get("/api/v1/districts/ak/upper/", **HEADERS)
    assert len(resp.json()) == 3
    resp = client.get("/api/v1/districts/ak/lower/", **HEADERS)
    assert len(resp.json()) == 5


@pytest.mark.django_db
def test_since_truncation(client):
    resp = client.get("/api/v1/bills/?updated_since=2020-01-01 11:21:12", **HEADERS)
    assert resp.status_code == 200


@pytest.mark.django_db
def test_search_window_message(client):
    resp = client.get("/api/v1/bills/?search_window=term:2020&state=ca", **HEADERS)
    assert resp.status_code == 400
    assert b"invalid search_window" in resp.content
