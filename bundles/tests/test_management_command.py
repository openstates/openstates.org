import pytest
from django.core.management import call_command
from graphapi.tests.utils import populate_db
from bundles.models import Bundle


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_basic_creation():
    call_command("manage_bundle", "test", name="Test Bundle", search="Moose")

    bundle = Bundle.objects.get(slug="test")
    assert bundle.name == "Test Bundle"
    assert bundle.bills.count() == 1


@pytest.mark.django_db
def test_update():
    call_command("manage_bundle", "test", name="Test Bundle", search="cheese")

    bundle = Bundle.objects.get(slug="test")
    assert bundle.name == "Test Bundle"
    assert bundle.bills.count() == 0

    call_command("manage_bundle", "test", name="Test Bundle", search="gorgonzola")
    assert bundle.bills.count() == 1
