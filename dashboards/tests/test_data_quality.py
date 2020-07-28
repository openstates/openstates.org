import datetime
import pytest
from django.core.management import call_command
from dashboards.management.commands.data_quality import (
    average_number_data,
    vote_data,
    total_bills_per_session,
    no_sources,
    bill_subjects,
    bills_versions,
    DataQualityReport,
)
from testutils.factories import create_test_bill, create_test_vote


@pytest.mark.django_db
def test_avg_number_data(django_assert_num_queries, kansas):
    # one bill with 0 of everything, another with 10 of everything
    create_test_bill("2020", "upper")
    create_test_bill(
        "2020", "upper", sponsors=10, versions=10, actions=10, votes=10, documents=10
    )
    upper = kansas.organizations.get(classification="upper")
    with django_assert_num_queries(5):
        data = average_number_data("KS", "2020", upper)
    assert data == {
        "average_actions_per_bill": 5,
        "average_documents_per_bill": 5,
        "average_sponsors_per_bill": 5,
        "average_versions_per_bill": 5,
        "average_votes_per_bill": 5,
        "max_actions_per_bill": 10,
        "max_documents_per_bill": 10,
        "max_sponsors_per_bill": 10,
        "max_versions_per_bill": 10,
        "max_votes_per_bill": 10,
        "min_actions_per_bill": 0,
        "min_documents_per_bill": 0,
        "min_sponsors_per_bill": 0,
        "min_versions_per_bill": 0,
        "min_votes_per_bill": 0,
    }


@pytest.mark.django_db
def test_vote_data(django_assert_num_queries, kansas):
    # two bills without votesr
    b = create_test_bill("2020", "upper")
    create_test_vote(b, yes_count=1)  # without voter
    create_test_vote(b, yes_count=1, yes_votes=["A", "B"])  # bad count
    b = create_test_bill("2020", "upper")
    create_test_vote(b, yes_count=1)  # without voters
    create_test_vote(b, yes_count=1, yes_votes=["A", "B"])  # bad count
    create_test_vote(b, yes_count=2, yes_votes=["A", "B"])  # good count
    create_test_vote(b, no_count=2, no_votes=["A"])  # bad count
    upper = kansas.organizations.get(classification="upper")
    with django_assert_num_queries(4):
        data = vote_data("KS", "2020", upper)
    assert data == {"total_votes_bad_counts": 3, "total_votes_without_voters": 2}


@pytest.mark.django_db
def test_bills_per_session(django_assert_num_queries, kansas):
    upper = kansas.organizations.get(classification="upper")

    b = create_test_bill("2020", "upper")
    b.actions.create(
        description="First", order=1, organization=upper, date="2020-01-01"
    )
    b.actions.create(
        description="First", order=1, organization=upper, date="2020-11-01"
    )

    with django_assert_num_queries(2):
        data = total_bills_per_session("KS", "2020", upper)
    assert len(data) == 4
    assert data["total_bills"] == 1
    assert data["earliest_action_date"].month == 1
    assert data["latest_action_date"].month == 11
    assert data["latest_bill_created_date"].day == datetime.date.today().day


@pytest.mark.django_db
def test_no_sources(django_assert_num_queries, kansas):
    create_test_bill("2020", "upper", votes=1)
    create_test_bill("2020", "upper", sources=1, votes=5)

    upper = kansas.organizations.get(classification="upper")

    with django_assert_num_queries(1):
        data = no_sources("KS", "2020", upper)
    assert data == {"total_bills_no_sources": 1, "total_votes_no_sources": 6}


@pytest.mark.django_db
def test_bill_subjects(django_assert_num_queries, kansas):
    create_test_bill("2020", "upper", subjects=["A", "B", "C"])
    create_test_bill("2020", "upper", subjects=["A", "B"])
    create_test_bill("2020", "upper", subjects=[])

    upper = kansas.organizations.get(classification="upper")

    with django_assert_num_queries(2):
        data = bill_subjects("KS", "2020", upper)
    assert data == {
        "number_of_bills_without_subjects": 1,
        "number_of_subjects_in_chamber": 3,
    }


@pytest.mark.django_db
def test_bill_versions(django_assert_num_queries, kansas):
    create_test_bill("2020", "upper", versions=1)
    create_test_bill("2020", "upper", versions=4)
    create_test_bill("2020", "upper")
    create_test_bill("2020", "upper")

    upper = kansas.organizations.get(classification="upper")
    with django_assert_num_queries(1):
        data = bills_versions("KS", "2020", upper)
    assert data == {"total_bills_without_versions": 2}


@pytest.mark.django_db
def test_full_command(django_assert_num_queries, kansas):
    for session in ("2019", "2020"):
        for chamber in ("upper", "lower"):
            create_test_bill(
                session,
                chamber,
                sponsors=10,
                versions=10,
                actions=10,
                votes=100,
                documents=10,
            )
            for n in range(100):
                create_test_bill(session, chamber)

    # Unsure about the exact query count here, as lots of these queries are checkpoints, etc.
    # but 91 for 2 sessions & 2 chambers seems OK and was stable with changing number of bills
    # and votes
    with django_assert_num_queries(91):
        call_command("data_quality", "KS")

    assert DataQualityReport.objects.count() == 4
