import pytest

# from django.core.management import call_command
from people_admin.utils import check_sponsorships  # , check_votes, update_unmatched
from testutils.factories import create_test_bill  # , create_test_vote


@pytest.mark.django_db
def test_check_sponsorships(django_assert_num_queries, kansas):
    # create two bills for the sponsor
    create_test_bill("2020", "upper")
    create_test_bill("2020", "upper", sponsors=1)
    create_test_bill("2020", "upper", sponsors=1)
    session = kansas.legislative_sessions.get(identifier="2020")

    with django_assert_num_queries(1):
        missing = check_sponsorships(session)
        assert missing == {"Someone": 2}
