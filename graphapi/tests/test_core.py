import pytest
from graphapi.schema import schema
from opencivicdata.core.models import Organization, Person
from .utils import populate_db


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_jurisdictions(django_assert_num_queries):
    with django_assert_num_queries(2):
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
    with django_assert_num_queries(4):
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
    with django_assert_num_queries(4):
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
    with django_assert_num_queries(5):
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
    with django_assert_num_queries(5):
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
def test_people_by_member_of(django_assert_num_queries):
    ak_house = Organization.objects.get(jurisdiction__name='Alaska', classification='lower')
    with django_assert_num_queries(2):
        result = schema.execute(''' {
            people(memberOf: "%s") {
                edges {
                    node {
                        name
                    }
                }
            }
        }
    ''' % ak_house.id)
    assert result.errors is None
    assert len(result.data['people']['edges']) == 4


@pytest.mark.django_db
def test_people_by_ever_member_of(django_assert_num_queries):
    ak_house = Organization.objects.get(jurisdiction__name='Alaska', classification='lower')
    with django_assert_num_queries(2):
        result = schema.execute(''' {
            people(everMemberOf: "%s") {
                edges {
                    node {
                        name
                    }
                }
            }
        }
    ''' % ak_house.id)
    assert result.errors is None
    # one extra person (Ellen Evil) is added as a former member of the House
    assert len(result.data['people']['edges']) == 5


@pytest.mark.django_db
def test_people_by_district():
    ak_house = Organization.objects.get(jurisdiction__name='Alaska', classification='lower')
    result = schema.execute(''' {
        ones: people(memberOf: "%s", district: "1") {
            edges { node { name } }
        }
        fives: people(everMemberOf: "%s", district: "5") {
            edges { node { name } }
        }
        bad: people(district: "1") {
            edges { node { name } }
        }
    }
    ''' % (ak_house.id, ak_house.id))
    assert "'district' parameter requires" in result.errors[0].message
    assert len(result.data['ones']['edges']) == 1
    assert len(result.data['fives']['edges']) == 1
    assert result.data['bad'] is None


@pytest.mark.django_db
def test_people_by_name():
    result = schema.execute(''' {
        people(name: "Hank") {
            edges { node { name } }
        }
    }
    ''')
    assert result.errors is None
    assert len(result.data['people']['edges']) == 1


@pytest.mark.django_db
def test_people_by_party():
    result = schema.execute(''' {
        dems: people(party: "Democratic") {
            edges { node { name } }
        }
        reps: people(party: "Republican") {
            edges { node { name } }
        }
    }
    ''')
    assert result.errors is None
    assert len(result.data['dems']['edges']) == 3
    assert len(result.data['reps']['edges']) == 4


# @pytest.mark.django_db
# def test_people_by_location():
#     # TODO: not implemented yet
#     pass


@pytest.mark.django_db
def test_people_num_queries(django_assert_num_queries):
    with django_assert_num_queries(8):
        result = schema.execute(''' {
        people {
            edges {
                node {
                    name
                    image
                    identifiers { identifier }
                    otherNames { name }
                    links { url }
                    sources { url }
                    contactDetails { value label }
                    currentMemberships {
                        post {
                            label
                            division {
                                id
                            }
                        }
                        organization { name }
                    }
                }
            }
        }
        }''')
    assert result.errors is None
    assert len(result.data['people']['edges']) == 8
    total_memberships = 0
    for person in result.data['people']['edges']:
        total_memberships += len(person['node']['currentMemberships'])
    assert total_memberships == 16      # 8 chambers + 8 parties


@pytest.mark.django_db
def test_person_by_id(django_assert_num_queries):
    person = Person.objects.get(name='Bob Birch')
    with django_assert_num_queries(7):
        result = schema.execute(''' {
        person(id:"%s") {
            name
            image
            identifiers { identifier }
            otherNames { name }
            links { url }
            sources { url }
            contactDetails { value label }
            currentMemberships {
                post {
                    label
                    division {
                        id
                    }
                }
                organization { name }
            }
        }
        }''' % person.id)
    assert result.errors is None
    assert result.data['person']['name'] == 'Bob Birch'
    assert len(result.data['person']['currentMemberships']) == 2

    division = None
    for membership in result.data['person']['currentMemberships']:
        if membership['post']:
            division = membership['post']['division']
            break
    assert division['id'] == 'ocd-division/country:us/state:Alaska/district:2'


@pytest.mark.django_db
def test_organization_by_id(django_assert_num_queries):
    # get targets
    leg = Organization.objects.get(jurisdiction__name='Wyoming', classification='legislature')
    sen = Organization.objects.get(jurisdiction__name='Wyoming', classification='upper')

    # 1 query for legislature, 1 query each for children, identifier, names, links, sources
    # 1 query for senate w/ parent
    with django_assert_num_queries(8):
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
