import pytest
from django.core.management import call_command
from opencivicdata.core.models import Jurisdiction, Division, Organization
from opencivicdata.legislative.models import Bill, LegislativeSession, VoteEvent
from ..models import Change


@pytest.mark.django_db
def setup():
    call_command("history_install")


@pytest.fixture
def session():
    d = Division.objects.create(id="ocd-division/country:us/state:ak", name="Alaska")
    j = Jurisdiction.objects.create(name="Alaska", id="ak", division=d)
    s = LegislativeSession.objects.create(identifier="2020", jurisdiction=j)
    return s


@pytest.fixture
def org():
    j = Jurisdiction.objects.get()
    return Organization.objects.create(
        jurisdiction=j, name="House", classification="lower"
    )


@pytest.mark.django_db
def test_bill_insert(session):
    b = Bill.objects.create(
        title="Test bill.", identifier="SB 1", legislative_session=session
    )
    assert Change.objects.count() == 1
    bh = Change.objects.get()
    assert bh.object_id == b.id
    assert bh.table_name == "opencivicdata_bill"
    assert bh.old is None
    assert bh.new["title"] == "Test bill."
    assert bh.new["identifier"] == "SB 1"


@pytest.mark.django_db
def test_bill_update(session):
    b = Bill.objects.create(
        title="mistake", identifier="SB 1", legislative_session=session
    )
    b.title = "corrected"
    b.save()

    assert Change.objects.count() == 2
    update = Change.objects.order_by("event_time")[1]
    assert set(update.old.keys()) == {"title", "updated_at"}
    assert update.old["title"] == "mistake"
    assert update.new["title"] == "corrected"


@pytest.mark.django_db
def test_bill_delete(session):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    b.delete()

    assert Change.objects.count() == 2
    delete = Change.objects.order_by("event_time")[1]
    assert delete.old["identifier"] == "SB 1"
    assert delete.new is None


@pytest.mark.django_db
def test_bill_action_insert(session, org):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    b.actions.create(
        description="introduced", date="2020-01-01", order=1, organization=org
    )
    assert Change.objects.count() == 2
    action = Change.objects.order_by("event_time")[1]
    assert action.old is None
    assert action.object_id == b.id
    assert action.new["description"] == "introduced"
    assert action.table_name == "opencivicdata_billaction"


@pytest.mark.django_db
def test_bill_action_update(session, org):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    a = b.actions.create(
        description="introduced", date="2020-01-01", order=1, organization=org
    )
    a.classification = ["introduced"]
    a.save()

    assert Change.objects.count() == 3
    action = Change.objects.order_by("event_time")[2]
    assert action.old == {}
    assert action.new["classification"] == ["introduced"]
    assert action.object_id == b.id
    assert action.table_name == "opencivicdata_billaction"


@pytest.mark.django_db
def test_bill_action_delete(session, org):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    a = b.actions.create(
        description="introduced", date="2020-01-01", order=1, organization=org
    )
    a.delete()

    assert Change.objects.count() == 3
    action = Change.objects.order_by("event_time")[2]
    assert action.old["description"] == "introduced"
    assert action.new is None
    assert action.object_id == b.id
    assert action.table_name == "opencivicdata_billaction"


# NOTE:
# these next tests are for objects that don't have a direct object_id, and are special cased
# in the pl/pgsql code, we don't need to check *all* the functionality, but lets make sure
# they link to the right parent id


@pytest.mark.django_db
def test_bill_versionlink_add(session, org):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    v = b.versions.create(note="first printing", date="2020-01-01")
    v.links.create(url="https://example.com")

    history = Change.objects.order_by("event_time")
    assert len(history) == 3
    # table names and object_id are recorded correctly
    assert history[0].object_id == history[1].object_id
    assert history[2].object_id == str(v.id)
    assert history[2].table_name == "opencivicdata_billversionlink"


@pytest.mark.django_db
def test_bill_documentlink_add(session, org):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    v = b.documents.create(note="fiscal note", date="2020-01-01")
    v.links.create(url="https://example.com")

    history = Change.objects.order_by("event_time")
    assert len(history) == 3
    # table names and object_id are recorded correctly
    assert history[0].object_id == history[1].object_id
    assert history[2].object_id == str(v.id)
    assert history[2].table_name == "opencivicdata_billdocumentlink"


@pytest.mark.django_db
def test_bill_actionrelatedentity_add(session, org):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    a = b.actions.create(
        description="introduced", date="2020-01-01", order=1, organization=org
    )
    a.related_entities.create(name="someone", entity_type="person")

    history = Change.objects.order_by("event_time")
    assert len(history) == 3
    # table names and object_id are recorded correctly
    assert history[0].object_id == history[1].object_id
    assert history[2].object_id == str(a.id)
    assert history[2].table_name == "opencivicdata_billactionrelatedentity"


# vote tests similarly do not need to test the actual behavior, just that they work


@pytest.mark.django_db
def test_vote_objects_history(session, org):
    v = VoteEvent.objects.create(
        identifier="test vote",
        start_date="2020-01-01",
        legislative_session=session,
        organization=org,
    )
    v.counts.create(option="yes", value=1)
    v.votes.create(option="yes", voter_name="someone")
    v.sources.create(url="https://example.com")
    history = Change.objects.order_by("event_time")
    assert len(history) == 4
    assert (
        history[0].object_id
        == history[1].object_id
        == history[2].object_id
        == history[3].object_id
    )
    # table names and object_id are recorded correctly
    assert history[0].table_name == "opencivicdata_voteevent"
    assert history[1].table_name == "opencivicdata_votecount"
    assert history[2].table_name == "opencivicdata_personvote"
    assert history[3].table_name == "opencivicdata_votesource"
