import pytest
from django.contrib.auth.models import User
from openstates.data.models import Person
from people_admin.models import UnmatchedName, NameStatus
import json


@pytest.fixture
def admin_user():
    return User.objects.create(username="admin", is_staff=True)


@pytest.mark.django_db
def test_apply_match_matches(client, django_assert_num_queries, kansas, admin_user):
    p = Person.objects.create(name="Samuel L. Jackson")

    # kansas is a test fixture, it has some fake data attached we can use
    session = kansas.legislative_sessions.get(identifier="2020")
    UnmatchedName.objects.create(
        id=1, session=session, name="Sam Jackson", sponsorships_count=5, votes_count=5
    )

    apply_data = {
        "match_data": {"unmatchedId": 1, "button": "Match", "matchedId": p.id}
    }
    client.force_login(admin_user)
    with django_assert_num_queries(4):
        resp = client.post(
            "/admin/people/matcher/update/",
            json.dumps(apply_data),
            content_type="application/json",
        )
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # get refreshed object from database
    matched = UnmatchedName.objects.get()
    assert matched.status == NameStatus.MATCHED_PERSON
    assert matched.matched_person_id == p.id


@pytest.mark.django_db
def test_apply_match_ignore(client, django_assert_num_queries, kansas, admin_user):
    session = kansas.legislative_sessions.get(identifier="2020")
    UnmatchedName.objects.create(
        id=2, session=session, name="Eva Green", sponsorships_count=16, votes_count=7
    )

    match_data = {"match_data": {"unmatchedId": 2, "button": "Ignore", "matchedId": ""}}
    client.force_login(admin_user)
    with django_assert_num_queries(4):
        # client can be used to mock GET/POST/etc.
        resp = client.post(
            "/admin/people/matcher/update/",
            json.dumps(match_data),
            content_type="application/json",
        )
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # get refreshed object from database
    matched = UnmatchedName.objects.get()
    assert matched.status == NameStatus.IGNORED


@pytest.mark.django_db
def test_apply_match_source_error(
    client, django_assert_num_queries, kansas, admin_user
):
    session = kansas.legislative_sessions.get(identifier="2020")
    UnmatchedName.objects.create(
        id=3,
        session=session,
        name="David Tennant",
        sponsorships_count=10,
        votes_count=2,
    )

    match_data = {
        "match_data": {"unmatchedId": 3, "button": "Source Error", "matchedId": ""}
    }
    client.force_login(admin_user)
    with django_assert_num_queries(4):
        resp = client.post(
            "/admin/people/matcher/update/",
            json.dumps(match_data),
            content_type="application/json",
        )
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # get refreshed object from database
    matched = UnmatchedName.objects.get()
    assert matched.status == NameStatus.SOURCE_ERROR


@pytest.mark.django_db
def test_apply_match_404(client, django_assert_num_queries, admin_user):
    client.force_login(admin_user)
    with django_assert_num_queries(3):
        match_data = {
            "match_data": {"unmatchedId": 9999, "button": "Match", "matchedId": "1"}
        }
        resp = client.post(
            "/admin/people/matcher/update/",
            json.dumps(match_data),
            content_type="application/json",
        )
    assert resp.status_code == 404
