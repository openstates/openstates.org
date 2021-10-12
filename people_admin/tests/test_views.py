import pytest
from testutils.factories import create_test_person
from django.contrib.auth.models import User, Permission
from openstates.data.models import Person, Organization
from people_admin.models import UnmatchedName, NameStatus, DeltaSet
from people_admin.views import MATCHER_PERM, EDIT_PERM, RETIRE_PERM
import json


@pytest.fixture
def admin_user():
    u = User.objects.create(username="admin")
    user_permissions = list(
        Permission.objects.filter(
            codename__in=[
                p.split(".")[1] for p in (MATCHER_PERM, EDIT_PERM, RETIRE_PERM)
            ]
        ).values_list("id", flat=True)
    )
    u.user_permissions.set(user_permissions)
    return u


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
    with django_assert_num_queries(6):
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
    with django_assert_num_queries(6):
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
    with django_assert_num_queries(6):
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
    with django_assert_num_queries(5):
        match_data = {
            "match_data": {"unmatchedId": 9999, "button": "Match", "matchedId": "1"}
        }
        resp = client.post(
            "/admin/people/matcher/update/",
            json.dumps(match_data),
            content_type="application/json",
        )
    assert resp.status_code == 404


@pytest.mark.django_db
def test_people_list(client, django_assert_num_queries, admin_user, kansas):
    house = Organization.objects.get(name="Kansas House")
    senate = Organization.objects.get(name="Kansas Senate")
    sam = create_test_person("Sam Jackson", org=house, party="Democratic", district="1")
    sam.identifiers.create(scheme="twitter", identifier="@SamuelLJackson")
    sam.offices.create(voice="555-555-5555", classification="capitol")
    create_test_person("Bosephorous Fogg", org=house, party="Republican", district="2")
    create_test_person("Cran Crumble", org=senate, party="Republican", district="A")
    client.force_login(admin_user)
    with django_assert_num_queries(7):
        resp = client.get("/admin/people/ks/")
    assert resp.status_code == 200
    people = resp.context["context"]["current_people"]
    assert len(people) == 3
    sam_data = [p for p in people if p["name"] == "Sam Jackson"][0]
    assert sam_data["district"] == "1"
    assert sam_data["twitter"] == "@SamuelLJackson"
    assert sam_data["capitol_voice"] == "555-555-5555"


@pytest.mark.django_db
def test_retire_person(client, django_assert_num_queries, admin_user, kansas):
    house = Organization.objects.get(name="Kansas House")
    sam = create_test_person("Sam Jackson", org=house, party="Democratic", district="1")

    retire_data = {
        "id": sam.id,
        "name": sam.name,
        "reason": "ran for new office",
        "retirementDate": "2021-01-01",
        "isDead": False,
        "vacantSeat": True,
    }
    client.force_login(admin_user)
    with django_assert_num_queries(6):
        resp = client.post(
            "/admin/people/retire/",
            json.dumps(retire_data),
            content_type="application/json",
        )
        assert resp.status_code == 200

    ds = DeltaSet.objects.get()
    assert "retire Sam Jackson" == ds.name
    assert ds.person_retirements.all().count() == 1
    retirement = ds.person_retirements.get()
    assert retirement.person_id == sam.id
    assert retirement.reason == "ran for new office"
    assert retirement.date == "2021-01-01"
    assert retirement.is_vacant
    assert retirement.is_dead is False
