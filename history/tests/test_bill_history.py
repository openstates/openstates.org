import pytest
from opencivicdata.core.models import Jurisdiction, Division, Organization
from opencivicdata.legislative.models import Bill, LegislativeSession
from ..models import BillHistory


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
    assert BillHistory.objects.count() == 1
    bh = BillHistory.objects.get()
    assert bh.bill_id == b.id
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

    assert BillHistory.objects.count() == 2
    update = BillHistory.objects.order_by("event_time")[1]
    assert set(update.old.keys()) == {"title", "updated_at"}
    assert update.old["title"] == "mistake"
    assert update.new["title"] == "corrected"


@pytest.mark.django_db
def test_bill_delete(session):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    b.delete()

    assert BillHistory.objects.count() == 2
    delete = BillHistory.objects.order_by("event_time")[1]
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
    assert BillHistory.objects.count() == 2
    action = BillHistory.objects.order_by("event_time")[1]
    assert action.old is None
    assert action.bill_id == b.id
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

    assert BillHistory.objects.count() == 3
    action = BillHistory.objects.order_by("event_time")[2]
    assert action.old == {}
    assert action.new["classification"] == ["introduced"]
    assert action.bill_id == b.id
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

    assert BillHistory.objects.count() == 3
    action = BillHistory.objects.order_by("event_time")[2]
    assert action.old["description"] == "introduced"
    assert action.new is None
    assert action.bill_id == b.id
    assert action.table_name == "opencivicdata_billaction"


# NOTE:
# these next tests are for objects that don't have a direct bill_id, and are special cased
# in the pl/pgsql code, we don't need to check *all* the functionality, but lets make sure
# they link to the right bill id


@pytest.mark.django_db
def test_bill_versionlink_add(session, org):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    v = b.versions.create(note="first printing", date="2020-01-01")
    v.links.create(url="https://example.com")

    history = BillHistory.objects.order_by("event_time")
    assert len(history) == 3
    # table names and bill_id are recorded correctly
    assert history[0].bill_id == history[1].bill_id == history[2].bill_id
    assert history[0].table_name == "opencivicdata_bill"
    assert history[1].table_name == "opencivicdata_billversion"
    assert history[2].table_name == "opencivicdata_billversionlink"


@pytest.mark.django_db
def test_bill_documentlink_add(session, org):
    b = Bill.objects.create(
        title="title", identifier="SB 1", legislative_session=session
    )
    v = b.documents.create(note="fiscal note", date="2020-01-01")
    v.links.create(url="https://example.com")

    history = BillHistory.objects.order_by("event_time")
    assert len(history) == 3
    # table names and bill_id are recorded correctly
    assert history[0].bill_id == history[1].bill_id == history[2].bill_id
    assert history[0].table_name == "opencivicdata_bill"
    assert history[1].table_name == "opencivicdata_billdocument"
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

    history = BillHistory.objects.order_by("event_time")
    assert len(history) == 3
    assert history[0].bill_id == history[1].bill_id == history[2].bill_id
    # table names and bill_id are recorded correctly
    assert history[0].table_name == "opencivicdata_bill"
    assert history[1].table_name == "opencivicdata_billaction"
    assert history[2].table_name == "opencivicdata_billactionrelatedentity"
