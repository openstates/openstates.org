import pytest
from opencivicdata.core.models import Jurisdiction, Division
from opencivicdata.legislative.models import Bill, LegislativeSession
from ..models import BillHistory


@pytest.fixture
def session():
    d = Division.objects.create(id="ocd-division/country:us/state:ak", name="Alaska")
    j = Jurisdiction.objects.create(name="Alaska", id="ak", division=d)
    s = LegislativeSession.objects.create(identifier="2020", jurisdiction=j)
    return s


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
