import pytest
from openstates.data.models import Person
from people_admin.models import UnmatchedName, NameStatus
import json


@pytest.mark.django_db
def test_apply_match_matches(client, django_assert_num_queries, kansas):
    p = Person.objects.create(name="Samuel L. Jackson")

    # kansas is a test fixture, it has some fake data attached we can use
    session = kansas.legislative_sessions.get(identifier="2020")
    UnmatchedName.objects.create(
        id=1, session=session, name="Sam Jackson", sponsorships_count=5, votes_count=5
    )

    apply_data = {
        "match_data": {"unmatchedId": 1, "button": "Match", "matchedId": p.id}
    }
    with django_assert_num_queries(2):
        # client can be used to mock GET/POST/etc.
        resp = client.post("/admin/people/matcher/update/", json.dumps(apply_data))
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # get refreshed object from database
    matched = UnmatchedName.objects.get()
    assert matched.status == NameStatus.MATCHED_PERSON
    assert matched.matched_person_id == p.id


@pytest.mark.django_db
def test_apply_match_ignore(client, django_assert_num_queries, kansas):
    session = kansas.legislative_sessions.get(identifier="2020")
    UnmatchedName.objects.create(
        id=2, session=session, name="Eva Green", sponsorships_count=16, votes_count=7
    )

    match_data = {"match_data": {"unmatchedId": 2, "button": "Ignore", "matchedId": ""}}
    with django_assert_num_queries(1):
        # client can be used to mock GET/POST/etc.
        resp = client.post("/admin/people/matcher/update/", json.dumps(match_data))
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # get refreshed object from database
    matched = UnmatchedName.objects.get()
    assert matched.status == NameStatus.IGNORED


@pytest.mark.django_db
def test_apply_match_source_error(client, django_assert_num_queries, kansas):
    session = kansas.legislative_sessions.get(identifier="2020")
    UnmatchedName.objects.create(
        id=3,
        session=session,
        name="David Tennant",
        sponsorships_count=10,
        votes_count=2
    )

    match_data = {
        "match_data": {"unmatchedId": 3, "button": "Source Error", "matchedId": ""}
    }
    with django_assert_num_queries(1):
        resp = client.post("/admin/people/matcher/update/", json.dumps(match_data))
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # get refreshed object from database
    matched = UnmatchedName.objects.get()
    assert matched.status == NameStatus.SOURCE_ERROR


@pytest.mark.django_db
def test_apply_match_404(client, django_assert_num_queries):
    with django_assert_num_queries(1):
        match_data = (
            '"{"match_data":{"unmatchedId":9999,"button":"Match","matchedId":"1"}}"'
        )
        resp = client.post("/admin/people/matcher/update/", match_data)
    assert resp.status_code == 404
