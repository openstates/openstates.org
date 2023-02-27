import pytest

from testutils.fixtures import kansas  # noqa
from graphapi.tests.utils import populate_db, populate_unicam


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        populate_db()
        populate_unicam()
