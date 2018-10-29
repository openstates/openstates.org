import pytest
from graphapi.tests.utils import populate_db
from .models import LegacyBillMapping
from opencivicdata.core.models import Person
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
def test_metadata_detail(client, django_assert_num_queries):
    with django_assert_num_queries(4):
        resp = client.get('/api/v1/metadata/ak/')
        assert resp.status_code == 200
        # TODO: test fields


@pytest.mark.django_db
def test_metadata_list(client, django_assert_num_queries):
    with django_assert_num_queries(4):
        resp = client.get('/api/v1/metadata/')
        assert resp.status_code == 200


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
    with django_assert_num_queries(15):
        resp = client.get('/api/v1/bills/?per_page=10')
        assert len(resp.json()) == 10
        assert resp.status_code == 200


@pytest.mark.django_db
def test_bill_list_state_param(client):
    wy = client.get('/api/v1/bills/?state=wy')
    ak = client.get('/api/v1/bills/?state=ak')
    assert len(wy.json()) + len(ak.json()) == 26


@pytest.mark.django_db
def test_bill_list_chamber_param(client):
    wy = client.get('/api/v1/bills/?state=wy')
    upper = client.get('/api/v1/bills/?state=wy&chamber=upper')
    lower = client.get('/api/v1/bills/?state=wy&chamber=lower')
    assert len(upper.json()) + len(lower.json()) == len(wy.json())


@pytest.mark.django_db
def test_bill_list_bill_id_param(client):
    hb1 = client.get('/api/v1/bills/?bill_id=HB 1')
    assert len(hb1.json()) == 1


@pytest.mark.django_db
def test_bill_list_q_param(client):
    moose = client.get('/api/v1/bills/?q=moose')
    assert len(moose.json()) == 1
    assert moose.json()[0]['title'] == 'Moose Freedom Act'


@pytest.mark.django_db
def test_bill_list_search_window_param(client):
    wy = client.get('/api/v1/bills/?state=wy')
    session2017 = client.get('/api/v1/bills/?state=wy&search_window=session:2017')
    session2018 = client.get('/api/v1/bills/?state=wy&search_window=session:2018')
    session_now = client.get('/api/v1/bills/?state=wy&search_window=session')
    assert len(session2017.json()) + len(session2018.json()) == len(wy.json())
    assert session2018.json() == session_now.json()


@pytest.mark.django_db
def test_bill_list_updated_since_param(client):
    since = client.get('/api/v1/bills/?updated_since=2018-01-01')
    assert len(since.json()) == 26
    since = client.get('/api/v1/bills/?updated_since=2038-01-01')
    assert len(since.json()) == 0


@pytest.mark.django_db
def test_bill_list_sort(client):
    all = client.get('/api/v1/bills/?sort=created_at').json()
    assert all[0]['created_at'] >= all[10]['created_at'] >= all[-1]['created_at']

    some_bill = Bill.objects.all()[16]
    some_bill.title = 'latest updated'
    some_bill.save()
    all = client.get('/api/v1/bills/?sort=updated_at').json()
    assert all[0]['updated_at'] >= all[10]['updated_at'] >= all[-1]['updated_at']
    assert all[0]['title'] == 'latest updated'


@pytest.mark.django_db
def test_legislator_detail(client, django_assert_num_queries):
    leg = Person.objects.get(name='Amanda Adams')
    leg.identifiers.create(scheme='legacy_openstates', identifier='AKL000001')

    with django_assert_num_queries(8):
        resp = client.get('/api/v1/legislators/AKL000001/')
        assert resp.status_code == 200
        # TODO: test fields


@pytest.mark.django_db
def test_legislator_list_basic(client, django_assert_num_queries):
    with django_assert_num_queries(8):
        resp = client.get('/api/v1/legislators/')
        assert resp.status_code == 200


@pytest.mark.django_db
def test_legislator_list_params(client, django_assert_num_queries):
    # check state filter
    resp = client.get('/api/v1/legislators/')
    assert len(resp.json()) == 8
    resp = client.get('/api/v1/legislators/?state=wy')
    assert len(resp.json()) == 2

    # check chamber filter
    resp = client.get('/api/v1/legislators/?state=ak&chamber=upper')
    assert len(resp.json()) == 2
    resp = client.get('/api/v1/legislators/?state=ak&chamber=lower')
    assert len(resp.json()) == 4

    # district filter
    resp = client.get('/api/v1/legislators/?district=1')
    assert len(resp.json()) == 3


# TODO: need mock data for this in graphapi tests
# @pytest.mark.django_db
# def test_legislator_geo(client, django_assert_num_queries):
#     pass


@pytest.mark.django_db
def test_districts_list(client, django_assert_num_queries):
    with django_assert_num_queries(1):
        resp = client.get('/api/v1/districts/ak/')
        assert resp.status_code == 200
        assert len(resp.json()) == 7
        # TODO: test fields

    # test filtering by URL
    resp = client.get('/api/v1/districts/ak/upper/')
    assert len(resp.json()) == 2
    resp = client.get('/api/v1/districts/ak/lower/')
    assert len(resp.json()) == 5
