import os
import csv
import json
import datetime
import tempfile
import zipfile
import uuid
import boto3
import base62
from django.core.management.base import BaseCommand
from django.db.models import F, Count, Avg
from openstates_metadata import STATES_BY_NAME
from openstates.data.models import (
    LegislativeSession,
    Bill,
    BillAbstract,
    BillAction,
    BillTitle,
    BillIdentifier,
    RelatedBill,
    BillSponsorship,
    BillDocument,
    BillVersion,
    BillDocumentLink,
    BillVersionLink,
    BillSource,
    VoteEvent,
    PersonVote,
    VoteCount,
    VoteSource,
)
from utils.common import abbr_to_jid
from utils.orgs import get_chambers_from_abbr
from collections import defaultdict
from statistics import mean

# Loads the global bill array with all bills from given state and session to use
#   when creating the json
def load_bills(state, session):
    bills = Bill.objects.filter(legislative_session__jurisdiction_id=abbr_to_jid(state), legislative_session__identifier=session).prefetch_related("actions",
        "sponsorships", "votes", "votes__counts", "sources", "documents", "versions", "votes__votes")
    return bills


def get_available_sessions(state):
    return sorted(
        s.identifier
        for s in LegislativeSession.objects.filter(jurisdiction_id=abbr_to_jid(state))
    )

def total_bills_per_session(bills, chambers):
    total_bills_per_session = defaultdict(list)
    for chamber in chambers:
        chamber_name = chamber.classification
        total_bills = bills.filter(from_organization=chamber).count()
        # Set variables to empty strings in case any info is blank
        latest_bill_created_date = ""
        latest_action_date = ""
        earliest_action_date = ""

        if total_bills > 0:
            latest_bill = bills.filter(from_organization=chamber).latest("created_at")
            latest_bill_created_date = latest_bill.created_at.strftime("%Y-%m-%d")
            bill_with_latest_action = bills.filter(from_organization=chamber).latest("actions__date")
            # In case bills don't have actions
            if bill_with_latest_action.actions.count() > 0:
                bill_with_latest_action_id = bill_with_latest_action.identifier
                latest_action = bill_with_latest_action.actions.latest("date")
                latest_action_date = latest_action.date

            # Earliest Action
            bill_with_earliest_action = bills.filter(from_organization=chamber).earliest("actions__date")
            # In case bills don't have actions
            if bill_with_earliest_action.actions.count() > 0:
                bill_with_earliest_action_id = bill_with_earliest_action.identifier
                earliest_action = bill_with_earliest_action.actions.earliest("date")
                earliest_action_date = earliest_action.date

        total_bills_per_session[chamber_name].append({
            "chamber": chamber_name,
            "total_bills": total_bills,
            "latest_bill_created_date": latest_bill_created_date,
            "latest_action_date": latest_action_date,
            "earliest_action_date": earliest_action_date}
        )
    return total_bills_per_session


def average_number_data(bills, chambers):
    average_num_data = defaultdict(list)

    for chamber in chambers:
        chamber_name = chamber.classification
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

        for bill in bills.filter(from_organization=chamber):
            total_sponsorships_per_bill.append(bill.sponsorships.count())
            total_actions_per_bill.append(bill.actions.count())
            total_votes_per_bill.append(bill.votes.count())
            total_documents_per_bill.append(bill.documents.count())
            total_versions_per_bill.append(bill.versions.count())

        average_sponsors_per_bill = round(mean(total_sponsorships_per_bill))
        average_actions_per_bill = round(mean(total_actions_per_bill))
        average_votes_per_bill = round(mean(total_votes_per_bill))
        average_documents_per_bill = round(mean(total_documents_per_bill))
        average_versions_per_bill = round(mean(total_versions_per_bill))

        min_sponsors_per_bill = round(min(total_actions_per_bill))
        max_sponsors_per_bill = round(max(total_actions_per_bill))

        min_actions_per_bill = round(min(total_actions_per_bill))
        max_actions_per_bill = round(max(total_actions_per_bill))

        min_votes_per_bill = round(min(total_votes_per_bill))
        max_votes_per_bill = round(max(total_votes_per_bill))

        min_documents_per_bill = round(min(total_documents_per_bill))
        max_documents_per_bill = round(max(total_documents_per_bill))

        min_versions_per_bill = round(min(total_versions_per_bill))
        max_versions_per_bill = round(max(total_versions_per_bill))

        average_num_data[chamber_name].append({
            "chamber": chamber_name,
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
            "max_versions_per_bill": max_versions_per_bill}
        )
    return average_num_data


def no_sources(bills, chambers):
    no_sources_data = defaultdict(list)
    for chamber in chambers:
        chamber_name = chamber.classification
        total_bills_no_sources = bills.filter(from_organization=chamber, sources=None).count()
        total_votes_no_sources = bills.filter(from_organization=chamber, votes__sources=None).count()
        no_sources_data[chamber_name].append({
            "chamber": chamber_name,
            "total_bills_no_sources": total_bills_no_sources,
            "total_votes_no_sources": total_votes_no_sources}
        )
    return no_sources_data


def bill_subjects(bills, chambers):
    bill_subjects_data = defaultdict(list)
    for chamber in chambers:
        chamber_name = chamber.classification
        overall_number_of_subjects = bills.distinct("subject").values_list("subject", flat=True).count()
        number_of_subjects = bills.filter(from_organization=chamber).distinct("subject").values_list("subject", flat=True).count()
        number_of_bills_without_subjects = bills.filter(from_organization=chamber, subject=None).count()
        bill_subjects_data[chamber_name].append({
            "chamber": chamber_name,
            "overall_number_of_subjects": overall_number_of_subjects,
            "number_of_subjects": number_of_subjects,
            "number_of_bills_without_subjects": number_of_bills_without_subjects}
        )
    return bill_subjects_data

def bills_versions(bills, chambers):
    bill_version_data = defaultdict(list)
    for chamber in chambers:
        chamber_name = chamber.classification
        bills_without_versions = bills.filter(from_organization=chamber, versions=None).count()
        bill_version_data[chamber_name].append({
            "chamber": chamber_name,
            "total_bills_without_versions": bills_without_versions}
        )

    return bill_version_data

def vote_data(bills, chambers):
    bill_vote_data = defaultdict(list)
    for chamber in chambers:
        chamber_name = chamber.classification
        # votes without any voters
        total_votes_without_voters = bills.filter(from_organization=chamber, votes__votes=None).values_list("votes").count()
        # votes (which do have voters, as to not include above category)
        #   but where yes/no count do not match actual voters
        total_votes_where_votes_dont_match_voters = 0
        bills_with_votes_with_voters = bills.filter(from_organization=chamber).exclude(votes__votes=None)
        for b in bills_with_votes_with_voters:
            for vote_object in b.votes.all():
                total_yes = 0
                total_no = 0
                total_absent = 0
                total_excused = 0
                total_not_voting = 0
                total_other = 0

                voter_count_yes = 0
                voter_count_no = 0
                voter_count_absent = 0
                voter_count_excused = 0
                voter_not_voting = 0
                voter_count_other = 0

                vote_counts = vote_object.counts.all()
                votes = vote_object.votes.all()
                # Parsing through vote_counts
                for count in vote_counts:
                    if "yes" == count.option:
                        total_yes = count.value
                    elif "no" == count.option:
                        total_no = count.value
                    elif "absent" == count.option:
                        total_absent = count.value
                    elif "excused" == count.option:
                        total_excused = count.value
                    elif "not voting" == count.option:
                        total_not_voting = count.value
                    elif "other" == count.option:
                        total_other = count.value
                    else:
                        print("Other option found in vote_counts: ", count)
                        print(count.__dict__)
                # Parsing through voters and adding up their votes
                for voter in votes:
                    if voter.option == "yes":
                        voter_count_yes += 1
                    elif voter.option == "no":
                        voter_count_no += 1
                    elif voter.option == "absent":
                        voter_count_absent += 1
                    elif voter.option == "excused":
                        voter_count_excused += 1
                    elif voter.option == "abstain":
                        voter_not_voting += 1
                    elif voter.option == "other":
                        voter_count_other += 1
                    else:
                        print(voter.option)
                # Checking to see if votes and vote counts match
                if (voter_count_yes != 0 and voter_count_yes != total_yes) or (voter_count_no != 0 and voter_count_no != total_no):
                    total_votes_where_votes_dont_match_voters += 1
        bill_vote_data[chamber_name].append({
            "total_votes_without_voters": total_votes_without_voters,
            "total_votes_where_votes_dont_match_voters": total_votes_where_votes_dont_match_voters}
        )


    return bill_vote_data


def write_json_to_file(filename, data):
    with open(filename, "w") as file:
        file.write(data)

# Example command
# docker-compose run --rm django poetry run ./manage.py data_quality Virginia
class Command(BaseCommand):
    help = "export data quality as a json"

    def add_arguments(self, parser):
        parser.add_argument("state")
        # parser.add_argument("sessions", nargs="*")
        # parser.add_argument("--all-sessions", action="store_true")


    def handle(self, *args, **options):
        state = options["state"]
        sessions = get_available_sessions(state)
        chambers = get_chambers_from_abbr(state)
        for session in sessions:
            # Resets bills inbetween every session
            bills = load_bills(state, session)
            if bills.count() > 0:
                bills_per_session_data = total_bills_per_session(bills, chambers)
                average_num_data = average_number_data(bills, chambers)
                bill_version_data = bills_versions(bills, chambers)
                no_sources_data = no_sources(bills, chambers)
                bill_subjects_data = bill_subjects(bills, chambers)
                bill_vote_data = vote_data(bills, chambers)

                overall_json_data = json.dumps({
                    "bills_per_session_data": dict(bills_per_session_data),
                    "average_num_data": dict(average_num_data),
                    "bill_version_data": dict(bill_version_data),
                    "no_sources_data": dict(no_sources_data),
                    "bill_vote_data": dict(bill_vote_data),
                    "bill_subjects_data": dict(bill_subjects_data)
                })
                filename = f"{state}_{session}_data_quality.json"
                write_json_to_file(filename, overall_json_data)