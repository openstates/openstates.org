import pytest
from graphapi.tests.utils import populate_db
from bundles.models import Bundle
from openstates.data.models import Bill


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_bundle_view(client, django_assert_num_queries):
    bundle = Bundle.objects.create(slug="test", name="Test Bundle")
    for b in Bill.objects.all():
        bundle.bills.add(b)
    with django_assert_num_queries(2):
        resp = client.get("/bundles/test/")
    assert resp.status_code == 200
    assert resp.context["bundle"] == bundle
    assert resp.context["total_bills"] == Bill.objects.count()
    assert sorted(resp.context["bills_by_state"].keys()) == ["Alaska", "Wyoming"]
