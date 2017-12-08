import pytest
from graphapi.schema import schema
from opencivicdata.core.models import Organization
from .utils import populate_db


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_jurisdictions(django_assert_num_queries):
    with django_assert_num_queries(1):
        result = schema.execute(''' {
            jurisdictions {
                edges {
                    node {
                        name
                    }
            }
        }
        }
    ''')
    assert result.errors is None
    assert result.data['jurisdictions']['edges'][0]['node']['name'] == 'Alaska'
    assert result.data['jurisdictions']['edges'][1]['node']['name'] == 'Wyoming'


@pytest.mark.django_db
def test_jurisdictions_num_queries(django_assert_num_queries):
    with django_assert_num_queries(3):
        result = schema.execute(''' {
            jurisdictions {
                edges {
                    node {
                        name
                        legislativeSessions {
                            edges { node { identifier } }
                        }
                        organizations {
                            edges { node { name } }
                        }
                    }
            }
        }
        }
    ''')
    assert result.errors is None
    assert len(result.data['jurisdictions']['edges'][0]['node']
               ['legislativeSessions']['edges']) == 2
    assert len(result.data['jurisdictions']['edges'][0]['node']['organizations']['edges']) == 3


@pytest.mark.django_db
def test_jurisdictions_num_queries_subquery(django_assert_num_queries):
    # same as test_jurisdictions_num_queries but with slightly more complex filtering on nodes
    with django_assert_num_queries(3):
        result = schema.execute(''' {
            jurisdictions {
                edges {
                    node {
                        name
                        legislativeSessions(first: 1) {
                            edges { node { identifier } }
                        }
                        organizations(classification: "legislature") {
                            edges { node { name } }
                        }
                    }
            }
        }
        }
    ''')
    assert result.errors is None
    assert len(result.data['jurisdictions']['edges'][0]['node']
               ['legislativeSessions']['edges']) == 1
    assert len(result.data['jurisdictions']['edges'][0]['node']['organizations']['edges']) == 1


@pytest.mark.django_db
def test_jurisdiction_by_id(django_assert_num_queries):
    with django_assert_num_queries(3):
        result = schema.execute(''' {
            jurisdiction(id:"ocd-jurisdiction/country:us/state:wy") {
                name
                legislativeSessions(first: 1) {
                    edges { node { identifier } }
                }
                organizations(classification: "legislature") {
                    edges { node { name } }
                }
            }
        }
    ''')
    assert result.errors is None
    assert len(result.data['jurisdiction']['legislativeSessions']['edges']) == 1
    assert len(result.data['jurisdiction']['organizations']['edges']) == 1


@pytest.mark.django_db
def test_jurisdiction_by_name(django_assert_num_queries):
    with django_assert_num_queries(3):
        result = schema.execute(''' {
            jurisdiction(name:"Wyoming") {
                name
                legislativeSessions(first: 1) {
                    edges { node { identifier } }
                }
                organizations(classification: "legislature") {
                    edges { node { name } }
                }
            }
        }
    ''')
    assert result.errors is None
    assert len(result.data['jurisdiction']['legislativeSessions']['edges']) == 1
    assert len(result.data['jurisdiction']['organizations']['edges']) == 1


@pytest.mark.django_db
def test_people_by_member_of():
    pass

@pytest.mark.django_db
def test_people_by_ever_member_of():
    pass

@pytest.mark.django_db
def test_people_by_district():
    pass

@pytest.mark.django_db
def test_people_by_name():
    pass

@pytest.mark.django_db
def test_people_by_party():
    pass

@pytest.mark.django_db
def test_people_by_location():
    pass

@pytest.mark.django_db
def test_people_num_queries():
    pass

@pytest.mark.django_db
def test_person_num_queries():
    pass

@pytest.mark.django_db
def test_person_current_memberships():
    pass


@pytest.mark.django_db
def test_organization_num_queries(django_assert_num_queries):
    # get targets
    leg = Organization.objects.get(jurisdiction__name='Wyoming', classification='legislature')
    sen = Organization.objects.get(jurisdiction__name='Wyoming', classification='upper')

    # 1 query for legislature, 1 query each for children, identifier, names, links, sources
    # 1 query for senate w/ parent
    with django_assert_num_queries(7):
        result = schema.execute(''' {
            leg: organization(id: "%s") {
                name
                classification
                children(classification: "upper") {
                    edges { node { classification } }
                }
                identifiers { identifier }
                otherNames { name }
                links { url }
                sources { url }
            }
            senate: organization(id: "%s") {
                name
                parent {
                    name
                }
            }
        }
    ''' % (leg.id, sen.id))
    assert result.errors is None
    assert len(result.data['leg']['children']['edges']) == 1
    assert result.data['senate']['parent']['name'] == 'Wyoming Legislature'
