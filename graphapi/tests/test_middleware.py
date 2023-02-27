import pytest
from graphapi.schema import schema
from ..middleware import QueryProtectionMiddleware


def test_simple_costs(django_assert_num_queries):
    result = schema.execute(
        """ {
        bill(jurisdiction:"ocd-jurisdiction/country:us/state:ak/government",
             session:"2018",
             identifier:"HB 1") {
            title
        }

        bills(first:100) { edges { node { title } } }

        jurisdictions { edges { node {
            first: organizations(first: 3) { edges { node { name } } }
            last: organizations(last: 3) { edges { node { name } } }
        } } }
    }""",
        middleware=[QueryProtectionMiddleware(0)],
    )  # max cost to 0 so everything errors
    assert len(result.errors) == 3
    # one item
    assert "(1)" in str(result.errors[0])
    # 100 bills
    assert "(100)" in str(result.errors[1])
    # each jurisdiction has 6 items beneath it
    assert "(6)" in str(result.errors[2])


def test_fragment_cost(django_assert_num_queries):
    result = schema.execute(
        """
        fragment JurisdictionFields on JurisdictionNode {
            first: organizations(first: 3) { edges { node { name } } }
            last: organizations(last: 3) { edges { node { name } } }
        }

        query jurisdictionsQuery { jurisdictions { edges { node { ...JurisdictionFields }}}}
    """,
        middleware=[QueryProtectionMiddleware(0)],
    )
    assert len(result.errors) == 1
    assert "(6)" in str(result.errors[0])
