import datetime
from django.core.management.base import BaseCommand
from django import db
from openstates.data.models import LegislativeSession, Bill, VoteEvent
from utils.cli import yield_state_sessions
from utils.common import abbr_to_jid
from utils.orgs import get_chambers_from_abbr
import pytz
from statistics import mean
from dashboards.models import DataQualityReport
from django.db.models import Max, Min, Count, Q


def bill_qs(state, session, chamber):
    bills = Bill.objects.filter(
        legislative_session__jurisdiction_id=abbr_to_jid(state),
        legislative_session__identifier=session,
        from_organization=chamber,
    )
    return bills


def vote_qs(state, session, chamber):
    return VoteEvent.objects.filter(
        legislative_session__jurisdiction_id=abbr_to_jid(state),
        legislative_session__identifier=session,
        organization=chamber,
    )


def clean_date(action_date):
    if isinstance(action_date, str):
        action_date = datetime.datetime.strptime(action_date[:10], "%Y-%m-%d")
    if isinstance(action_date, datetime.datetime):
        return pytz.UTC.localize(action_date)


def total_bills_per_session(state, session, chamber):
    bills = bill_qs(state, session, chamber)
    total_bills = bills.count()
    # Set variables to empty strings in case any info is blank
    latest_bill_created_date = ""
    latest_action_date = ""
    earliest_action_date = ""
    if total_bills > 0:
        bill_queries = bills.aggregate(
            latest_bill_created=Min("created_at"),
            latest_action_date=Max("actions__date"),
            earliest_action_date=Min("actions__date"),
        )

        latest_bill_created_date = bill_queries["latest_bill_created"]
        latest_action_date = clean_date(bill_queries["latest_action_date"])
        earliest_action_date = clean_date(bill_queries["earliest_action_date"])

    total_bills_per_session = {
        "total_bills": total_bills,
        "latest_bill_created_date": latest_bill_created_date,
        "latest_action_date": latest_action_date,
        "earliest_action_date": earliest_action_date,
    }
    return total_bills_per_session


def average_number_data(state, session, chamber):
    bills = bill_qs(state, session, chamber)
    total_sponsorships_per_bill = []
    total_actions_per_bill = []
    total_votes_per_bill = []
    total_documents_per_bill = []
    total_versions_per_bill = []

    average_sponsors_per_bill = 0
    average_actions_per_bill = 0
    average_votes_per_bill = 0
    average_documents_per_bill = 0
    average_versions_per_bill = 0

    min_sponsors_per_bill = 0
    max_sponsors_per_bill = 0

    min_actions_per_bill = 0
    max_actions_per_bill = 0

    min_votes_per_bill = 0
    max_votes_per_bill = 0

    min_documents_per_bill = 0
    max_documents_per_bill = 0

    min_versions_per_bill = 0
    max_versions_per_bill = 0

    sponsorships = bills.annotate(n=Count("sponsorships")).values_list("n", flat=True)
    actions = bills.annotate(n=Count("actions")).values_list("n", flat=True)
    documents = bills.annotate(n=Count("documents")).values_list("n", flat=True)
    versions = bills.annotate(n=Count("versions")).values_list("n", flat=True)
    votes = bills.annotate(n=Count("votes")).values_list("n", flat=True)

    for n_sponsorships, n_actions, n_docs, n_versions, n_votes in zip(
        sponsorships, actions, documents, versions, votes
    ):
        total_sponsorships_per_bill.append(n_sponsorships)
        total_actions_per_bill.append(n_actions)
        total_votes_per_bill.append(n_votes)
        total_documents_per_bill.append(n_docs)
        total_versions_per_bill.append(n_versions)

    if total_sponsorships_per_bill:
        average_sponsors_per_bill = round(mean(total_sponsorships_per_bill))
        min_sponsors_per_bill = round(min(total_sponsorships_per_bill))
        max_sponsors_per_bill = round(max(total_sponsorships_per_bill))

    if total_actions_per_bill:
        average_actions_per_bill = round(mean(total_actions_per_bill))
        min_actions_per_bill = round(min(total_actions_per_bill))
        max_actions_per_bill = round(max(total_actions_per_bill))

    if total_votes_per_bill:
        average_votes_per_bill = round(mean(total_votes_per_bill))
        min_votes_per_bill = round(min(total_votes_per_bill))
        max_votes_per_bill = round(max(total_votes_per_bill))

    if total_documents_per_bill:
        average_documents_per_bill = round(mean(total_documents_per_bill))
        min_documents_per_bill = round(min(total_documents_per_bill))
        max_documents_per_bill = round(max(total_documents_per_bill))

    if total_versions_per_bill:
        average_versions_per_bill = round(mean(total_versions_per_bill))
        min_versions_per_bill = round(min(total_versions_per_bill))
        max_versions_per_bill = round(max(total_versions_per_bill))

    average_num_data = {
        "average_sponsors_per_bill": average_sponsors_per_bill,
        "min_sponsors_per_bill": min_sponsors_per_bill,
        "max_sponsors_per_bill": max_sponsors_per_bill,
        "average_actions_per_bill": average_actions_per_bill,
        "min_actions_per_bill": min_actions_per_bill,
        "max_actions_per_bill": max_actions_per_bill,
        "average_votes_per_bill": average_votes_per_bill,
        "min_votes_per_bill": min_votes_per_bill,
        "max_votes_per_bill": max_votes_per_bill,
        "average_documents_per_bill": average_documents_per_bill,
        "min_documents_per_bill": min_documents_per_bill,
        "max_documents_per_bill": max_documents_per_bill,
        "average_versions_per_bill": average_versions_per_bill,
        "min_versions_per_bill": min_versions_per_bill,
        "max_versions_per_bill": max_versions_per_bill,
    }
    return average_num_data


def no_sources(state, session, chamber):
    bills = bill_qs(state, session, chamber)
    qs = bills.aggregate(
        total_bills_no_sources=Count("pk", filter=Q(sources=None)),
        total_votes_no_sources=Count(
            "pk", filter=~Q(votes=None) & Q(votes__sources=None)
        ),
    )
    return qs


def bill_subjects(state, session, chamber):
    all_subjs = set()
    bills = bill_qs(state, session, chamber)
    for subject in bills.values_list("subject", flat=True):
        all_subjs.update(subject)
    number_of_bills_without_subjects = bills.filter(subject=[]).count()
    bill_subjects_data = {
        "number_of_subjects_in_chamber": len(all_subjs),
        "number_of_bills_without_subjects": number_of_bills_without_subjects,
    }
    return bill_subjects_data


def bills_versions(state, session, chamber):
    bills = bill_qs(state, session, chamber)
    bills_without_versions = bills.filter(versions=None).count()
    bill_version_data = {"total_bills_without_versions": bills_without_versions}
    return bill_version_data


def vote_data(state, session, chamber):
    votes = vote_qs(state, session, chamber)
    # votes without any voters
    total_votes_without_voters = votes.filter(votes=None).count()
    # votes (which do have voters, as to not include above category)
    #   but where yes/no count do not match actual voters
    total_votes_bad_counts = 0

    votes = votes.exclude(votes=None).prefetch_related("counts", "votes")
    for vote in votes:
        yes_count = 0
        no_count = 0
        for pv in vote.votes.all():
            if pv.option == "yes":
                yes_count += 1
            elif pv.option == "no":
                no_count += 1
        for pv in vote.counts.all():
            if (pv.option == "yes" and pv.value != yes_count) or (
                pv.option == "no" and pv.value != no_count
            ):
                total_votes_bad_counts += 1

    bill_vote_data = {
        "total_votes_without_voters": total_votes_without_voters,
        "total_votes_bad_counts": total_votes_bad_counts,
    }

    return bill_vote_data


@db.transaction.atomic()
def create_dqr(state, session):
    chambers = get_chambers_from_abbr(state)
    for chamber in chambers:
        print(f"creating report for {chamber} in {state} {session}")
        if bill_qs(state, session, chamber).count() > 0:
            bills_per_session_data = total_bills_per_session(state, session, chamber)
            average_num_data = average_number_data(state, session, chamber)
            bill_version_data = bills_versions(state, session, chamber)
            no_sources_data = no_sources(state, session, chamber)
            bill_subjects_data = bill_subjects(state, session, chamber)
            bill_vote_data = vote_data(state, session, chamber)

            # update or save the report
            leg_session = LegislativeSession.objects.get(
                identifier=session, jurisdiction_id=abbr_to_jid(state)
            )
            DataQualityReport.objects.update_or_create(
                session=leg_session,
                chamber=chamber.classification,
                defaults={
                    **bills_per_session_data,
                    **average_num_data,
                    **bill_version_data,
                    **no_sources_data,
                    **bill_vote_data,
                    **bill_subjects_data,
                },
            )


# Example command
# docker-compose run --rm django poetry run ./manage.py data_quality VA
class Command(BaseCommand):
    help = "create data quality objects for dashboards"

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("--session", default=None)

    def handle(self, *args, **options):
        state = options["state"]
        session = options["session"]

        # 'all' grabs the first session from every state
        # 'all_sessions' grabs every session from every state
        for state, session in yield_state_sessions(state, session):
            create_dqr(state, session)
