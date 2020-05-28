import pytest
from graphapi.tests.utils import populate_db
from django.core.management import call_command
# from dashboards.models import DataQualityReport


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_total_queries(django_assert_num_queries):
    with django_assert_num_queries(40) as captured:
        call_command("data_quality", "AK")
    assert captured.captured_queries.count() == 40
