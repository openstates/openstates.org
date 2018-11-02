import pytest
from graphapi.schema import schema
from .utils import populate_db
from ..middleware import QueryProtectionMiddleware


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_metadata_counts(django_assert_num_queries):
    result = schema.execute(''' {
        bill(jurisdiction:"ocd-jurisdiction/country:us/state:ak/government",
             session:"2018",
             identifier:"HB 1") {
            title
        }

        bills(first:100) { edges { node { title } } }

        jurisdictions(first:10) { edges { node { 
            first: organizations(first: 3) { edges { node { name } } } 
            last: organizations(last: 3) { edges { node { name } } } 
        } } }
    }''', middleware=[QueryProtectionMiddleware()])
    assert result.errors is None
    assert False
