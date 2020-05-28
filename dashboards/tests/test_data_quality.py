import pytest
from graphapi.tests.utils import populate_db
from django.core.management import call_command
from utils.orgs import get_chambers_from_abbr
from dashboards.management.commands.data_quality import load_bills, average_number_data, vote_data, total_bills_per_session, no_sources, bill_subjects, bills_versions


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.mark.django_db
def test_avg_number_data_queries(django_assert_num_queries):
    state = "AK"
    session = "2018"
    bills = load_bills(state, session)
    chamber = get_chambers_from_abbr(state)[0]
    with django_assert_num_queries(10) as captured:
        average_number_data(bills, chamber)


@pytest.mark.django_db
def test_vote_data_queries(django_assert_num_queries):
    state = "AK"
    session = "2018"
    bills = load_bills(state, session)
    chamber = get_chambers_from_abbr(state)[0]
    with django_assert_num_queries(16) as captured:
        vote_data(bills, chamber)


@pytest.mark.django_db
def test_bills_per_session_queries(django_assert_num_queries):
    state = "AK"
    session = "2018"
    bills = load_bills(state, session)
    chamber = get_chambers_from_abbr(state)[0]
    with django_assert_num_queries(30) as captured:
        total_bills_per_session(bills, chamber)


@pytest.mark.django_db
def test_no_sources_queries(django_assert_num_queries):
    state = "AK"
    session = "2018"
    bills = load_bills(state, session)
    chamber = get_chambers_from_abbr(state)[0]
    with django_assert_num_queries(2) as captured:
        no_sources(bills, chamber)


@pytest.mark.django_db
def test_bill_subjects_queries(django_assert_num_queries):
    state = "AK"
    session = "2018"
    bills = load_bills(state, session)
    chamber = get_chambers_from_abbr(state)[0]
    with django_assert_num_queries(3) as captured:
        bill_subjects(bills, chamber)


@pytest.mark.django_db
def test_bill_versions_queries(django_assert_num_queries):
    state = "AK"
    session = "2018"
    bills = load_bills(state, session)
    chamber = get_chambers_from_abbr(state)[0]
    with django_assert_num_queries(1) as captured:
        bills_versions(bills, chamber)

# @pytest.mark.django_db
# def test_total_queries(django_assert_num_queries):
#     with django_assert_num_queries(40) as captured:
#         call_command("data_quality", "AK")