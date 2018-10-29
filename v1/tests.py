import pytest
from graphapi.tests.utils import populate_db
from .models import LegacyBillMapping
from opencivicdata.legislative.models import Bill


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_removed_views(client):
    resp = client.get('/api/v1/committees/')
    assert resp.status_code == 200
    assert resp.json() == []
    resp = client.get('/api/v1/events/')
    assert resp.status_code == 200
    assert resp.json() == []
    resp = client.get('/api/v1/committees/AKC000001/')
    assert resp.status_code == 404
    resp = client.get('/api/v1/events/AKE00000001/')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_metadata_list(client, django_assert_num_queries):
    with django_assert_num_queries(4):
        resp = client.get('/api/v1/metadata/')
        assert resp.status_code == 200
        # TODO: test fields


@pytest.mark.django_db
def test_metadata_detail(client, django_assert_num_queries):
    with django_assert_num_queries(4):
        resp = client.get('/api/v1/metadata/ak/')
        assert resp.status_code == 200
        # TODO: test fields


@pytest.mark.django_db
def test_bill_detail(client, django_assert_num_queries):
    with django_assert_num_queries(17):
        resp = client.get('/api/v1/bills/ak/2018/HB 1/')
        assert resp.status_code == 200
        # TODO: test fields

    # ensure that alternate forms work too
    new_resp = client.get('/api/v1/bills/ak/2018/lower/HB 1/')
    assert new_resp.json() == resp.json()

    # legacy ID
    LegacyBillMapping.objects.create(legacy_id='AKB00000001',
                                     bill=Bill.objects.get(identifier='HB 1'))
    assert client.get('/api/v1/bills/AKB00000001/').json() == resp.json()


@pytest.mark.django_db
def test_bill_list_basic(client, django_assert_num_queries):
    with django_assert_num_queries(17):
        resp = client.get('/api/v1/bills/?per_page=10')
        assert len(resp.json()) == 10
        assert resp.status_code == 200
        # TODO: test fields


@pytest.mark.django_db
def test_bill_list_params(client, django_assert_num_queries):
    pass


@pytest.mark.django_db
def test_legislator_detail(client, django_assert_num_queries):
    pass


@pytest.mark.django_db
def test_legislator_list_basic(client, django_assert_num_queries):
    pass


@pytest.mark.django_db
def test_legislator_list_params(client, django_assert_num_queries):
    pass


@pytest.mark.django_db
def test_legislator_geo(client, django_assert_num_queries):
    pass


@pytest.mark.django_db
def test_districts_list(client, django_assert_num_queries):
    pass
