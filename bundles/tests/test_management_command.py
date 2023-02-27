import pytest
from django.core.management import call_command
from bundles.models import Bundle


def test_basic_creation():
    call_command("manage_bundle", "test", name="Test Bundle", search="Moose")

    bundle = Bundle.objects.get(slug="test")
    assert bundle.name == "Test Bundle"
    assert bundle.bills.count() == 1


def test_update():
    call_command("manage_bundle", "test", name="Test Bundle", search="cheese")

    bundle = Bundle.objects.get(slug="test")
    assert bundle.name == "Test Bundle"
    assert bundle.bills.count() == 0

    call_command("manage_bundle", "test", name="Test Bundle", search="gorgonzola")
    assert bundle.bills.count() == 1
