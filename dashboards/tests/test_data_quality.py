import datetime
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
from openstates.data.models import (
    Jurisdiction,
)


def test_avg_number_data(django_assert_num_queries):
    # one bill with 0 of everything, another with 10 of everything
    jur = Jurisdiction.objects.get(name="Kansas")
    upper = jur.organizations.get(classification="upper")
    with django_assert_num_queries(5):
        data = average_number_data("KS", "2020", upper)
    assert data == {
        "average_actions_per_bill": 5,
        "average_documents_per_bill": 5,
        "average_sponsors_per_bill": 5,
        "average_versions_per_bill": 2,
        "average_votes_per_bill": 2,
        "max_actions_per_bill": 10,
        "max_documents_per_bill": 10,
        "max_sponsors_per_bill": 10,
        "max_versions_per_bill": 4,
        "max_votes_per_bill": 2,
        "min_actions_per_bill": 0,
        "min_documents_per_bill": 0,
        "min_sponsors_per_bill": 0,
        "min_versions_per_bill": 0,
        "min_votes_per_bill": 2,
    }


def test_vote_data(django_assert_num_queries):
    # two bills without votesr
    jur = Jurisdiction.objects.get(name="Kansas")
    upper = jur.organizations.get(classification="upper")
    with django_assert_num_queries(4):
        data = vote_data("KS", "2020", upper)
    assert data == {"total_votes_bad_counts": 0, "total_votes_without_voters": 4}


def test_bills_per_session(django_assert_num_queries):
    jur = Jurisdiction.objects.get(name="Kansas")
    upper = jur.organizations.get(classification="upper")

    with django_assert_num_queries(2):
        data = total_bills_per_session("KS", "2020", upper)
    assert len(data) == 4
    assert data["total_bills"] == 2
    assert data["earliest_action_date"].month == 1
    assert data["latest_action_date"].month == 1
    assert data["latest_bill_created_date"].day == datetime.date.today().day


def test_no_sources(django_assert_num_queries):
    jur = Jurisdiction.objects.get(name="Kansas")

    upper = jur.organizations.get(classification="upper")

    with django_assert_num_queries(1):
        data = no_sources("KS", "2020", upper)
    assert data == {"total_bills_no_sources": 2, "total_votes_no_sources": 4}


def test_bill_subjects(django_assert_num_queries):
    jur = Jurisdiction.objects.get(name="Kansas")

    upper = jur.organizations.get(classification="upper")

    with django_assert_num_queries(2):
        data = bill_subjects("KS", "2020", upper)
    assert data == {
        "number_of_bills_without_subjects": 0,
        "number_of_subjects_in_chamber": 1,
    }


def test_bill_versions(django_assert_num_queries):
    jur = Jurisdiction.objects.get(name="Kansas")

    upper = jur.organizations.get(classification="upper")
    with django_assert_num_queries(1):
        data = bills_versions("KS", "2020", upper)
    assert data == {"total_bills_without_versions": 1}


def test_full_command(django_assert_num_queries):
    # jur = Jurisdiction.objects.get(name="Kansas")

    # Unsure about the exact query count here, as lots of these queries are checkpoints, etc.
    # but 91 for 2 sessions & 2 chambers seems OK and was stable with changing number of bills
    # and votes
    with django_assert_num_queries(91):
        call_command("data_quality", "KS")

    assert DataQualityReport.objects.count() == 4
