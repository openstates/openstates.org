import datetime
from django.core.management.base import BaseCommand
from openstates.data.models import (
    LegislativeSession,
    Bill,
)
from utils.common import abbr_to_jid, states, sessions_with_bills
from utils.orgs import get_chambers_from_abbr
import pytz
from collections import defaultdict
from statistics import mean
from dashboards.models import DataQualityReport
from django.db.models import Avg, Max, Min, Count, Sum, Q


# Loads the global bill array with all bills from given state and session to use
def load_bills(state, session):
    bills = Bill.objects.filter(
        legislative_session__jurisdiction_id=abbr_to_jid(state),
        legislative_session__identifier=session,
    ).prefetch_related(
        "actions",
        "sponsorships",
        "votes",
        "votes__counts",
        "sources",
        "documents",
        "versions",
        "votes__votes",
    )
    return bills


def get_available_sessions(state):
    return sorted(
        s.identifier
        for s in LegislativeSession.objects.filter(jurisdiction_id=abbr_to_jid(state))
    )


def total_bills_per_session(bills, chamber):

    print("Generating bills per session")
    total_bills = bills.filter(from_organization=chamber).count()
    # Set variables to empty strings in case any info is blank
    latest_bill_created_date = ""
    latest_action_date = ""
    earliest_action_date = ""
    if total_bills > 0:

        bill_queries = bills.filter(from_organization=chamber).aggregate(
            test_latest_bill_created=Min("created_at"),
            test_latest_action_date=Max("actions__date"),
            test_earliest_action_date=Min("actions__date"),
        )

        latest_bill_created_date = bill_queries["test_earliest_action_date"]
        latest_action_date = bill_queries["test_latest_action_date"]
        earliest_action_date = bill_queries["test_earliest_action_date"]

        # latest_bill_created_date = latest_action_date[:10]
        latest_bill_created_date = datetime.datetime.strptime(
            latest_bill_created_date, "%Y-%m-%d"
        )
        latest_bill_created_date = pytz.UTC.localize(latest_bill_created_date)

        if latest_action_date:
            latest_action_date = latest_action_date[:10]
            latest_action_date = datetime.datetime.strptime(
                latest_action_date, "%Y-%m-%d"
            )
            latest_action_date = pytz.UTC.localize(latest_action_date)
        if earliest_action_date:
            earliest_action_date = earliest_action_date[:10]
            earliest_action_date = datetime.datetime.strptime(
                earliest_action_date, "%Y-%m-%d"
            )
            earliest_action_date = pytz.UTC.localize(earliest_action_date)

    total_bills_per_session = {
        "total_bills": total_bills,
        "latest_bill_created_date": latest_bill_created_date,
        "latest_action_date": latest_action_date,
        "earliest_action_date": earliest_action_date,
    }
    return total_bills_per_session


def average_number_data(bills, chamber):
    print("Generating average num data")
    average_num_data = defaultdict(list)

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

    # test = bills.aggregate(Count("sponsorships"))
    # test_max = round(max(test))
    # test_bills = bills.filter(from_organization=chamber).annotate(
    #     tot_sponsorships=Count("sponsorships"),
    #     tot_actions=Count("actions"),
    #     tot_documents=Count("documents"),
    #     tot_versions=Count("versions"),
    #     tot_votes=Count("votes"),
    # )

    for bill in bills.filter(from_organization=chamber):
        total_sponsorships_per_bill.append(bill.sponsorships.count())
        total_actions_per_bill.append(bill.actions.count())
        total_votes_per_bill.append(bill.votes.count())
        total_documents_per_bill.append(bill.documents.count())
        total_versions_per_bill.append(bill.versions.count())

    # for bill in test_bills:
    #     total_sponsorships_per_bill.append(bill.tot_sponsorships)
    #     total_actions_per_bill.append(bill.tot_actions)
    #     total_votes_per_bill.append(bill.tot_votes)
    #     total_documents_per_bill.append(bill.tot_documents)
    #     total_versions_per_bill.append(bill.tot_versions)

    if total_sponsorships_per_bill:
        average_sponsors_per_bill = round(mean(total_sponsorships_per_bill))
        min_sponsors_per_bill = round(min(total_actions_per_bill))
        max_sponsors_per_bill = round(max(total_actions_per_bill))

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


def no_sources(bills, chamber):
    print("Generating no source data")
    no_sources_data = defaultdict(list)
    total_bills_no_sources = bills.filter(
        from_organization=chamber, sources=None
    ).count()
    total_votes_no_sources = bills.filter(
        from_organization=chamber, votes__sources=None
    ).count()
    no_sources_data = {
        "total_bills_no_sources": total_bills_no_sources,
        "total_votes_no_sources": total_votes_no_sources,
    }
    return no_sources_data


def bill_subjects(bills, chamber):
    print("Generating bill subject data")
    bill_subjects_data = defaultdict(list)
    overall_number_of_subjects = (
        bills.distinct("subject").values_list("subject", flat=True).count()
    )
    number_of_subjects_in_chamber = (
        bills.filter(from_organization=chamber)
        .distinct("subject")
        .values_list("subject", flat=True)
        .count()
    )
    number_of_bills_without_subjects = bills.filter(
        from_organization=chamber, subject=None
    ).count()
    bill_subjects_data = {
        "overall_number_of_subjects": overall_number_of_subjects,
        "number_of_subjects_in_chamber": number_of_subjects_in_chamber,
        "number_of_bills_without_subjects": number_of_bills_without_subjects,
    }
    return bill_subjects_data


def bills_versions(bills, chamber):
    print("Generating bills version data")
    bill_version_data = defaultdict(list)
    bills_without_versions = bills.filter(
        from_organization=chamber, versions=None
    ).count()
    bill_version_data = {"total_bills_without_versions": bills_without_versions}
    return bill_version_data


def vote_data(bills, chamber):
    print("Generating vote data")
    bill_vote_data = defaultdict(list)
    # votes without any voters
    total_votes_without_voters = (
        bills.filter(from_organization=chamber, votes__votes=None)
        .values_list("votes")
        .count()
    )
    # votes (which do have voters, as to not include above category)
    #   but where yes/no count do not match actual voters
    total_votes_bad_counts = 0
    bills_with_votes_with_voters = bills.filter(from_organization=chamber).exclude(
        votes__votes=None
    )
    for b in bills_with_votes_with_voters:
        for vote_object in b.votes.all().prefetch_related("counts", "votes"):
            total_yes = 0
            total_no = 0

            voter_count_yes = 0
            voter_count_no = 0
            voter_count_absent = 0
            voter_count_excused = 0
            voter_not_voting = 0
            voter_count_other = 0

            vote_counts = vote_object.counts.all()
            # votes = vote_object.votes.all()

            # voter_count_query = vote_object.counts.aggregate(
            #     total_yes=Sum('value', filter=Q(option="yes")),
            #     total_no=Sum('value', filter=Q(option="no")),
            # )

            # total_yes = voter_count_query["total_yes"]
            # total_no = voter_count_query["total_no"]

            # Parsing through vote_counts
            for count in vote_counts:
                if "yes" == count.option:
                    total_yes = count.value
                elif "no" == count.option:
                    total_no = count.value

            voter_query = vote_object.votes.aggregate(
                voter_count_yes=Count("pk", filter=Q(option="yes")),
                voter_count_no=Count("pk", filter=Q(option="no"))
            )

            voter_count_yes = voter_query["voter_count_yes"]
            voter_count_no = voter_query["voter_count_no"]


            # Parsing through voters and adding up their votes
            # for voter in votes:
                # if voter.option == "yes":
                #     voter_count_yes += 1
                # elif voter.option == "no":
                #     voter_count_no += 1
                # elif voter.option == "absent":
                #     voter_count_absent += 1
                # elif voter.option == "excused":
                #     voter_count_excused += 1
                # elif voter.option == "abstain":
                #     voter_not_voting += 1
                # elif voter.option == "not voting":
                #     voter_not_voting += 1
                # elif voter.option == "other":
                #     voter_count_other += 1
            # Checking to see if votes and vote counts match
            if (voter_count_yes != 0 and voter_count_yes != total_yes) or (
                voter_count_no != 0 and voter_count_no != total_no
            ):
                total_votes_bad_counts += 1
    bill_vote_data = {
        "total_votes_without_voters": total_votes_without_voters,
        "total_votes_bad_counts": total_votes_bad_counts,
    }

    return bill_vote_data


def write_json_to_file(filename, data):
    with open(filename, "w") as file:
        file.write(data)


def create_dqr(state, session):
    bills = load_bills(state, session)
    chambers = get_chambers_from_abbr(state)
    for chamber in chambers:
        print("\n\n", f"creating report for {chamber} in {state} {session}")
        if bills.filter(from_organization=chamber).count() > 0:
            bills_per_session_data = total_bills_per_session(bills, chamber)

            average_num_data = average_number_data(bills, chamber)
            bill_version_data = bills_versions(bills, chamber)
            no_sources_data = no_sources(bills, chamber)
            bill_subjects_data = bill_subjects(bills, chamber)
            bill_vote_data = vote_data(bills, chamber)

            # Grabbing the Legislative Session object
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

    def handle(self, *args, **options):
        state = options["state"]
        # 'all' grabs the first session from every state
        # 'all_sessions' grabs every session from every state
        if state == "all" or state == "all_sessions":
            scrape_state = state
            for state in states:
                sessions = sessions_with_bills(abbr_to_jid(state.abbr))
                if len(sessions) > 0:
                    state = state.abbr.lower()
                    if scrape_state == "all_sessions":
                        for session in sessions:
                            session = session.identifier
                            create_dqr(state, session)
                    else:
                        session = sessions[0].identifier
                        create_dqr(state, session)
        else:
            sessions = get_available_sessions(state)
            for session in sessions:
                create_dqr(state, session)
