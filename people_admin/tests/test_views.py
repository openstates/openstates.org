import pytest
from openstates.data.models import Person
from people_admin.models import UnmatchedName, NameStatus


@pytest.mark.django_db
def test_apply_match_matches(client, django_assert_num_queries, kansas):
    p = Person.objects.create(name="Samuel L. Jackson")

    # kansas is a test fixture, it has some fake data attached we can use
    session = kansas.legislative_sessions.get(identifier="2020")
    UnmatchedName.objects.create(
        id=1, session=session, name="Sam Jackson", sponsorships_count=5, votes_count=5
    )
    with django_assert_num_queries(2):
        # client can be used to mock GET/POST/etc.
        resp = client.post(
            "/admin/people/matcher/update/1", {"match_id": p.id, "submit": "Match"}
        )
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}

    # get refreshed object from database
    matched = UnmatchedName.objects.get()
    assert matched.status == NameStatus.MATCHED_PERSON
    assert matched.matched_person_id == p.id


@pytest.mark.django_db
def test_apply_match_404(client, django_assert_num_queries):
    with django_assert_num_queries(1):
        resp = client.post(
            "/admin/people/matcher/update/9999", {"match_id": 1, "submit": "Match"}
        )
    assert resp.status_code == 404
