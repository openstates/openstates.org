import pytest
from graphapi.schema import schema
from openstates.data.models import Organization, Person
from .utils import populate_db


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_jurisdictions(django_assert_num_queries):
    with django_assert_num_queries(2):
        result = schema.execute(
            """ {
            jurisdictions {
                edges {
                    node {
                        name
                    }
            }
        }
        }
    """
        )
    assert result.errors is None
    assert result.data["jurisdictions"]["edges"][0]["node"]["name"] == "Alaska"
    assert result.data["jurisdictions"]["edges"][1]["node"]["name"] == "Wyoming"


@pytest.mark.django_db
def test_jurisdictions_num_queries(django_assert_num_queries):
    with django_assert_num_queries(4):
        result = schema.execute(
            """ {
            jurisdictions {
                edges {
                    node {
                        name
                        legislativeSessions {
                            edges { node { identifier } }
                        }
                        organizations(first: 50) {
                            edges { node { name } }
                        }
                    }
            }
        }
        }
    """
        )
    assert result.errors is None
    assert (
        len(
            result.data["jurisdictions"]["edges"][0]["node"]["legislativeSessions"][
                "edges"
            ]
        )
        == 2
    )
    assert (
        len(result.data["jurisdictions"]["edges"][0]["node"]["organizations"]["edges"])
        == 3
    )


@pytest.mark.django_db
def test_jurisdictions_num_queries_subquery(django_assert_num_queries):
    # same as test_jurisdictions_num_queries but with slightly more complex filtering on nodes
    with django_assert_num_queries(4):
        result = schema.execute(
            """ {
            jurisdictions {
                edges {
                    node {
                        name
                        legislativeSessions(first: 1) {
                            edges { node { identifier } }
                        }
                        organizations(classification: "legislature", first: 50) {
                            edges { node { name } }
                        }
                    }
            }
        }
        }
    """
        )
    assert result.errors is None
    assert (
        len(
            result.data["jurisdictions"]["edges"][0]["node"]["legislativeSessions"][
                "edges"
            ]
        )
        == 1
    )
    assert (
        len(result.data["jurisdictions"]["edges"][0]["node"]["organizations"]["edges"])
        == 1
    )


@pytest.mark.django_db
def test_jurisdiction_by_id(django_assert_num_queries):
    with django_assert_num_queries(5):
        result = schema.execute(
            """ {
            jurisdiction(id:"ocd-jurisdiction/country:us/state:wy/government") {
                name
                legislativeSessions(first: 1) {
                    edges { node { identifier } }
                }
                organizations(classification: "legislature", first: 50) {
                    edges { node { name } }
                }
            }
        }
    """
        )
    assert result.errors is None
    assert len(result.data["jurisdiction"]["legislativeSessions"]["edges"]) == 1
    assert len(result.data["jurisdiction"]["organizations"]["edges"]) == 1


@pytest.mark.django_db
def test_jurisdiction_by_name(django_assert_num_queries):
    with django_assert_num_queries(5):
        result = schema.execute(
            """ {
            jurisdiction(name:"Wyoming") {
                name
                legislativeSessions(first: 1) {
                    edges { node { identifier } }
                }
                organizations(classification: "legislature", first: 50) {
                    edges { node { name } }
                }
            }
        }
    """
        )
    assert result.errors is None
    assert len(result.data["jurisdiction"]["legislativeSessions"]["edges"]) == 1
    assert len(result.data["jurisdiction"]["organizations"]["edges"]) == 1


@pytest.mark.django_db
def test_jurisdiction_chambers_current_members(django_assert_num_queries):
    with django_assert_num_queries(5):
        result = schema.execute(
            """ {
            jurisdiction(name:"Wyoming") {
                chambers: organizations(classification:["upper", "lower"], first:2)
                { edges { node {
                    name
                    currentMemberships {
                        person { name }
                    }
                } }
                }
            }
        }
    """
        )
    assert result.errors is None
    assert len(result.data["jurisdiction"]["chambers"]["edges"]) == 2
    assert set(("Wyoming House", "Wyoming Senate")) == set(
        edge["node"]["name"]
        for edge in result.data["jurisdiction"]["chambers"]["edges"]
    )
    people = []
    for chamber in result.data["jurisdiction"]["chambers"]["edges"]:
        for m in chamber["node"]["currentMemberships"]:
            people.append(m["person"]["name"])
    assert len(people) == 2


@pytest.mark.django_db
def test_people_by_member_of(django_assert_num_queries):
    ak_house = Organization.objects.get(
        jurisdiction__name="Alaska", classification="lower"
    )
    with django_assert_num_queries(2):
        result = schema.execute(
            """ {
            people(memberOf: "%s", first: 50) {
                edges {
                    node {
                        name
                    }
                }
            }
        }
    """
            % ak_house.id
        )
    assert result.errors is None
    assert len(result.data["people"]["edges"]) == 4


@pytest.mark.django_db
def test_variable_people_by_member_of(django_assert_num_queries):
    ak_house = Organization.objects.get(
        jurisdiction__name="Alaska", classification="lower"
    )
    with django_assert_num_queries(2):
        result = schema.execute(
            """
            query peeps($f: Int){
                people(memberOf: "%s", first: $f) {
                    edges {
                        node {
                            name
                        }
                    }
                }
            }
        """
            % ak_house.id,
            variable_values={"f": 3},
        )
    assert result.errors is None
    assert len(result.data["people"]["edges"]) == 3


@pytest.mark.django_db
def test_people_by_ever_member_of(django_assert_num_queries):
    ak_house = Organization.objects.get(
        jurisdiction__name="Alaska", classification="lower"
    )
    with django_assert_num_queries(2):
        result = schema.execute(
            """ {
            people(everMemberOf: "%s", first:50) {
                edges {
                    node {
                        name
                    }
                }
            }
        }
    """
            % ak_house.id
        )
    assert result.errors is None
    # one extra person (Ellen Evil) is added as a former member of the House
    assert len(result.data["people"]["edges"]) == 5


@pytest.mark.django_db
def test_people_by_district():
    ak_house = Organization.objects.get(
        jurisdiction__name="Alaska", classification="lower"
    )
    result = schema.execute(
        """ {
        ones: people(memberOf: "%s", district: "1", first: 50) {
            edges { node { name } }
        }
        fives: people(everMemberOf: "%s", district: "5", first: 50) {
            edges { node { name } }
        }
        bad: people(district: "1", first: 50) {
            edges { node { name } }
        }
    }
    """
        % (ak_house.id, ak_house.id)
    )
    assert "'district' parameter requires" in result.errors[0].message
    assert len(result.data["ones"]["edges"]) == 1
    assert len(result.data["fives"]["edges"]) == 1
    assert result.data["bad"] is None


@pytest.mark.django_db
def test_people_by_division_id():
    # Note: uses a fake divisionId that has two reps (one retired), only one should be returned
    result = schema.execute(
        """ {
        people(divisionId: "ocd-division/country:us/state:ak/sldu:b", first: 50) {
            edges { node { name } }
        }
    }
    """
    )
    assert len(result.data["people"]["edges"]) == 1


@pytest.mark.django_db
def test_people_by_name():
    result = schema.execute(
        """ {
        people(name: "Hank", first: 50) {
            edges { node { name } }
        }
    }
    """
    )
    assert result.errors is None
    assert len(result.data["people"]["edges"]) == 1


@pytest.mark.django_db
def test_people_by_party():
    result = schema.execute(
        """ {
        dems: people(memberOf: "Democratic", first: 50) {
            edges { node { name } }
        }
        reps: people(memberOf: "Republican", first: 50) {
            edges { node { name } }
        }
    }
    """
    )
    assert result.errors is None
    assert len(result.data["dems"]["edges"]) == 3
    assert len(result.data["reps"]["edges"]) == 4


# @pytest.mark.django_db
# def test_people_by_location():
#     # TODO: need data to test with
#     pass


@pytest.mark.django_db
def test_people_num_queries(django_assert_num_queries):
    with django_assert_num_queries(8):
        result = schema.execute(
            """ {
        people(first: 50) {
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
        }"""
        )
    assert result.errors is None
    assert len(result.data["people"]["edges"]) == 9
    total_memberships = 0
    for person in result.data["people"]["edges"]:
        total_memberships += len(person["node"]["currentMemberships"])
    assert total_memberships == 16  # 8 chambers + 8 parties


@pytest.mark.django_db
def test_people_total_count(django_assert_num_queries):
    with django_assert_num_queries(2):
        result = schema.execute(
            """ {
        people(first: 50) {
            totalCount
            edges {
                node {
                    name
                }
            }
        }
        }"""
        )
    assert result.errors is None
    assert result.data["people"]["totalCount"] == 9
    assert len(result.data["people"]["edges"]) == 9

    with django_assert_num_queries(2):
        result = schema.execute(
            """ {
        people(first: 50, name: "Amanda") {
            totalCount
            edges {
                node {
                    name
                }
            }
        }
        }"""
        )
    assert result.errors is None
    assert result.data["people"]["totalCount"] == 1
    assert len(result.data["people"]["edges"]) == 1


@pytest.mark.django_db
def test_people_current_memberships_classification(django_assert_num_queries):
    with django_assert_num_queries(3):
        result = schema.execute(
            """ {
        people(first: 50) {
            edges {
                node {
                    currentMemberships(classification: "party") {
                        organization { name }
                    }
                }
            }
        }
        }"""
        )
    assert result.errors is None
    total_memberships = 0
    for person in result.data["people"]["edges"]:
        total_memberships += len(person["node"]["currentMemberships"])
    assert total_memberships == 8  # Only the 8 parties should be returned


@pytest.mark.django_db
def test_people_old_memberships(django_assert_num_queries):
    with django_assert_num_queries(3):
        result = schema.execute(
            """{
        people(first: 50) {
            edges {
                node {
                    oldMemberships {
                        organization { name }
                    }
                }
            }
        }
        }"""
        )
    assert result.errors is None
    old_memberships = 0
    for person in result.data["people"]["edges"]:
        old_memberships += len(person["node"]["oldMemberships"])
    assert old_memberships == 3  # three old memberships in test data right now


@pytest.mark.django_db
def test_person_by_id(django_assert_num_queries):
    person = Person.objects.get(name="Bob Birch")
    with django_assert_num_queries(7):
        result = schema.execute(
            """ {
        person(id:"%s") {
            name
            image
            primaryParty
            email
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
        }"""
            % person.id
        )
    assert result.errors is None
    assert result.data["person"]["name"] == "Bob Birch"
    assert result.data["person"]["primaryParty"] == "Republican"
    assert len(result.data["person"]["currentMemberships"]) == 2

    division = None
    for membership in result.data["person"]["currentMemberships"]:
        if membership["post"]:
            division = membership["post"]["division"]
            break
    assert division["id"] == "ocd-division/country:us/state:ak/sldl:2"


@pytest.mark.django_db
def test_person_email_shim(django_assert_num_queries):
    # email used to be available in contact_details, make sure they can still find it there
    person = Person.objects.get(name="Bob Birch")
    person.email = "bob@example.com"
    person.save()
    result = schema.execute(
        """ {
    person(id:"%s") {
        name
        email
        contactDetails { value note type }
    }
    }"""
        % person.id
    )
    assert result.errors is None
    assert result.data["person"]["name"] == "Bob Birch"
    assert result.data["person"]["email"] == "bob@example.com"
    assert result.data["person"]["contactDetails"][0] == {
        "value": "bob@example.com",
        "type": "email",
        "note": "Capitol Office",
    }


@pytest.mark.django_db
def test_organization_by_id(django_assert_num_queries):
    # get targets
    leg = Organization.objects.get(
        jurisdiction__name="Wyoming", classification="legislature"
    )
    sen = Organization.objects.get(jurisdiction__name="Wyoming", classification="upper")

    # 1 query for legislature, 1 query each for children, links, sources
    # 1 query for senate w/ parent
    with django_assert_num_queries(6):
        result = schema.execute(
            """ {
            leg: organization(id: "%s") {
                name
                classification
                children(classification: "upper", first: 50) {
                    edges { node { classification } }
                }
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
    """
            % (leg.id, sen.id)
        )
    assert result.errors is None
    assert len(result.data["leg"]["children"]["edges"]) == 1
    assert result.data["senate"]["parent"]["name"] == "Wyoming Legislature"


@pytest.mark.django_db
def test_people_by_updated_since():
    middle_date = Person.objects.all().order_by("updated_at")[2].updated_at

    result = schema.execute(
        """{
        all: people(updatedSince: "2017-01-01T00:00:00Z", last:50) {
            edges { node { name } }
        }
        some: people(updatedSince: "%s", first:50) {
            edges { node { name } }
        }
        none: people(updatedSince: "2030-01-01T00:00:00Z", first:50) {
            edges { node { name } }
        }
    }"""
        % middle_date
    )

    assert result.errors is None
    assert len(result.data["all"]["edges"]) == 9
    assert len(result.data["some"]["edges"]) == 7
    assert len(result.data["none"]["edges"]) == 0


@pytest.mark.django_db
def test_jurisdiction_fragment(django_assert_num_queries):
    with django_assert_num_queries(3):
        result = schema.execute(
            """
    fragment JurisdictionFields on JurisdictionNode {
      id
      name
      url
      legislativeSessions {
        edges {
          node {
            name
            startDate
            endDate
            classification
            identifier
          }
        }
      }
    }

    query jurisdictionsQuery {
      jurisdictions {
        edges {
          node {
            ...JurisdictionFields
          }
        }
      }
    }"""
        )
    assert result.errors is None
