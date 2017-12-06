import pytest
from graphapi.schema import schema
from .utils import populate_db


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_bill_by_id(django_assert_num_queries):
    with django_assert_num_queries(11):
        result = schema.execute(''' {
            bill(id:"ocd-bill/1") {
                title
                classification
                subject
                abstracts {
                    abstract
                }
                otherTitles {
                    title
                }
                otherIdentifiers {
                    identifier
                }
                actions {
                    description
                    organization {
                        name
                        classification
                    }
                }
                sponsorships {
                    name
                    classification
                }
                documents {
                    note
                    links { url }
                }
                versions {
                    note
                    links { url }
                }
                sources { url }
            }
        }''')

    assert result.errors is None
    assert result.data['bill']['title'] == 'Moose Freedom Act'
    assert result.data['bill']['classification'] == ['bill', 'constitutional amendment']
    assert result.data['bill']['subject'] == ['nature']
    assert len(result.data['bill']['abstracts']) == 2
    assert len(result.data['bill']['otherTitles']) == 3
    assert len(result.data['bill']['actions']) == 3
    assert result.data['bill']['actions'][0]['organization']['classification'] == 'lower'
    assert len(result.data['bill']['sponsorships']) == 2
    assert len(result.data['bill']['documents'][0]['links']) == 1
    assert len(result.data['bill']['versions'][0]['links']) == 2
    assert len(result.data['bill']['sources']) == 3


@pytest.mark.django_db
def test_bill_by_jurisdiction_id_session_identifier(django_assert_num_queries):
    with django_assert_num_queries(1):
        result = schema.execute(''' {
            bill(jurisdiction:"ocd-jurisdiction/country:us/state:ak",
                 session:"2018",
                 identifier:"HB 1") {
                title
            }
        }''')
        assert result.errors is None
        assert result.data['bill']['title'] == 'Moose Freedom Act'


@pytest.mark.django_db
def test_bill_by_jurisdiction_name_session_identifier(django_assert_num_queries):
    with django_assert_num_queries(1):
        result = schema.execute(''' {
            bill(jurisdiction:"Alaska", session:"2018", identifier:"HB 1") {
                title
            }
        }''')
        assert result.errors is None
        assert result.data['bill']['title'] == 'Moose Freedom Act'


@pytest.mark.django_db
def test_bill_by_jurisdiction_session_identifier_incomplete():
    result = schema.execute(''' {
        bill(jurisdiction:"Alaska", identifier:"HB 1") {
            title
        }
    }''')
    assert len(result.errors) == 1
    assert 'must either pass' in result.errors[0].message


@pytest.mark.django_db
def test_bill_by_jurisdiction_session_identifier_404():
    result = schema.execute(''' {
        bill(jurisdiction:"Alaska", session:"2018" identifier:"HB 404") {
            title
        }
    }''')
    assert len(result.errors) == 1
    assert 'does not exist' in result.errors[0].message


@pytest.mark.django_db
def test_bills_queries():
    pass


@pytest.mark.django_db
def test_bills_by_jurisdiction(django_assert_num_queries):
    with django_assert_num_queries(2):
        result = schema.execute(''' {
            ak: bills(jurisdiction:"Alaska") {
                edges { node { title } }
            }
            wy: bills(jurisdiction:"ocd-jurisdiction/country:us/state:wy") {
                edges { node { title } }
            }
        }''')
    assert result.errors is None
    # 26 total bills created
    assert len(result.data['ak']['edges'] + result.data['wy']['edges']) == 26


@pytest.mark.django_db
def test_bills_by_chamber(django_assert_num_queries):
    with django_assert_num_queries(2):
        result = schema.execute(''' {
            lower: bills(chamber:"lower") {
                edges { node { title } }
            }
            upper: bills(chamber:"upper") {
                edges { node { title } }
            }
        }''')
    assert result.errors is None
    # 26 total bills created
    assert len(result.data['lower']['edges'] + result.data['upper']['edges']) == 26


@pytest.mark.django_db
def test_bills_by_session(django_assert_num_queries):
    with django_assert_num_queries(2):
        result = schema.execute(''' {
            y2018: bills(session:"2018") {
                edges { node { title } }
            }
            y2017: bills(session:"2017") {
                edges { node { title } }
            }
        }''')
    assert result.errors is None
    # 26 total bills created
    assert len(result.data['y2017']['edges'] + result.data['y2018']['edges']) == 26


@pytest.mark.django_db
def test_bills_by_updated_since():
    pass

@pytest.mark.django_db
def test_bills_by_classification():
    pass

@pytest.mark.django_db
def test_bills_by_subject():
    pass

@pytest.mark.django_db
def test_bills_pagination():
    pass
