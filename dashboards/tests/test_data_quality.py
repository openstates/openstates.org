import random
import datetime
import pytest
from django.core.management import call_command
from openstates.data.models import (
    Division,
    Jurisdiction,
    Organization,
    LegislativeSession,
    Bill,
)
from dashboards.management.commands.data_quality import (
    average_number_data,
    vote_data,
    total_bills_per_session,
    no_sources,
    bill_subjects,
    bills_versions,
    DataQualityReport,
)


@pytest.fixture
def kansas():
    d = Division.objects.create(id="ocd-division/country:us/state:ks", name="Kansas")
    j = Jurisdiction.objects.create(
        id="ocd-jurisdiction/country:us/state:ks/government", name="Kansas", division=d
    )
    j.legislative_sessions.create(
        identifier="2019", name="2019", start_date="2019-01-01"
    )
    j.legislative_sessions.create(
        identifier="2020", name="2020", start_date="2020-01-01"
    )

    leg = Organization.objects.create(
        jurisdiction=j, classification="legislature", name="Kansas Legislature"
    )
    Organization.objects.create(
        jurisdiction=j, parent=leg, classification="lower", name="Kansas House"
    )
    Organization.objects.create(
        jurisdiction=j, parent=leg, classification="upper", name="Kansas Senate"
    )
    return j


def create_bill(
    session,
    chamber,
    *,
    sponsors=0,
    actions=0,
    votes=0,
    versions=0,
    documents=0,
    sources=0,
    subjects=None
):
    chamber = Organization.objects.get(classification=chamber)
    session = LegislativeSession.objects.get(identifier=session)
    b = Bill.objects.create(
        identifier="Bill " + str(random.randint(1000, 9000)),
        title="Random Bill",
        legislative_session=session,
        from_organization=chamber,
        subject=subjects or [],
    )
    for n in range(sponsors):
        b.sponsorships.create(name="Someone")
    for n in range(actions):
        b.actions.create(
            description="Something", order=n, organization=chamber, date="2020-06-01"
        )
    for n in range(votes):
        b.votes.create(
            identifier="A Vote Occurred",
            organization=chamber,
            legislative_session=session,
        )
    for n in range(versions):
        b.versions.create(note="Version")
    for n in range(documents):
        b.documents.create(note="Document")
    for n in range(sources):
        b.sources.create(url="http://example.com")
    return b


def create_test_vote(bill, *, yes_count=0, no_count=0, yes_votes=None, no_votes=None):
    vote = bill.votes.create(
        identifier="test vote",
        organization=bill.from_organization,
        legislative_session=bill.legislative_session,
    )
    vote.counts.create(option="yes", value=yes_count)
    vote.counts.create(option="no", value=no_count)
    for name in yes_votes or []:
        vote.votes.create(option="yes", voter_name=name)
    for name in no_votes or []:
        vote.votes.create(option="no", voter_name=name)


@pytest.mark.django_db
def test_avg_number_data(django_assert_num_queries, kansas):
    # one bill with 0 of everything, another with 10 of everything
    create_bill("2020", "upper")
    create_bill(
        "2020", "upper", sponsors=10, versions=10, actions=10, votes=10, documents=10
    )
    upper = kansas.organizations.get(classification="upper")
    with django_assert_num_queries(1):
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
    b = create_bill("2020", "upper")
    create_test_vote(b, yes_count=1)  # without voter
    create_test_vote(b, yes_count=1, yes_votes=["A", "B"])  # bad count
    b = create_bill("2020", "upper")
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

    b = create_bill("2020", "upper")
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
    create_bill("2020", "upper", votes=1)
    create_bill("2020", "upper", sources=1, votes=5)

    upper = kansas.organizations.get(classification="upper")

    with django_assert_num_queries(1):
        data = no_sources("KS", "2020", upper)
    assert data == {"total_bills_no_sources": 1, "total_votes_no_sources": 6}


@pytest.mark.django_db
def test_bill_subjects(django_assert_num_queries, kansas):
    create_bill("2020", "upper", subjects=["A", "B", "C"])
    create_bill("2020", "upper", subjects=["A", "B"])
    create_bill("2020", "upper", subjects=[])

    upper = kansas.organizations.get(classification="upper")

    with django_assert_num_queries(2):
        data = bill_subjects("KS", "2020", upper)
    assert data == {
        "number_of_bills_without_subjects": 1,
        "number_of_subjects_in_chamber": 3,
    }


@pytest.mark.django_db
def test_bill_versions(django_assert_num_queries, kansas):
    create_bill("2020", "upper", versions=1)
    create_bill("2020", "upper", versions=4)
    create_bill("2020", "upper")
    create_bill("2020", "upper")

    upper = kansas.organizations.get(classification="upper")
    with django_assert_num_queries(1):
        data = bills_versions("KS", "2020", upper)
    assert data == {"total_bills_without_versions": 2}


@pytest.mark.django_db
def test_full_command(django_assert_num_queries, kansas):
    for session in ("2019", "2020"):
        for chamber in ("upper", "lower"):
            create_bill(
                session,
                chamber,
                sponsors=10,
                versions=10,
                actions=10,
                votes=100,
                documents=10,
            )
            for n in range(100):
                create_bill(session, chamber)

    # Unsure about the exact query count here, as lots of these queries are checkpoints, etc.
    # but 71 for 2 sessions & 2 chambers seems OK and was stable with changing number of bills
    # and votes
    with django_assert_num_queries(71):
        call_command("data_quality", "KS")

    assert DataQualityReport.objects.count() == 4
