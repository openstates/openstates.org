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
    sobj = LegislativeSession.objects.get(
        jurisdiction_id=abbr_to_jid(state), identifier=session
    )
    bills = Bill.objects.filter(legislative_session=sobj).prefetch_related("actions", "sponsorships", "votes", "votes__counts", "sources")
    # for bill in Bill.objects.filter(legislative_session=sobj):
    #     bills.add(bill.select_related(
    #         "legislative_session",
    #         "legislative_session__jurisdiction",
    #         "from_organization",
    #         "searchable",
    #     ).prefetch_related(
    #         "abstracts",
    #         "other_titles",
    #         "other_identifiers",
    #         "actions",
    #         "related_bills",
    #         "sponsorships",
    #         "documents",
    #         "documents__links",
    #         "versions",
    #         "versions__links",
    #         "sources",
    #         "votes__votes",
    #     ))
    return bills


def get_available_sessions(state):
    return sorted(
        s.identifier
        for s in LegislativeSession.objects.filter(jurisdiction_id=abbr_to_jid(state))
    )

def total_bills_per_session(bills, chambers):
    total_bills_per_session = defaultdict(list)
    for chamber in chambers:
        chamber_name = chamber.name.lower()
        total_bills = bills.filter(from_organization=chamber).count()
        # Set variables to empty strings in case any info is blank
        latest_bill = ""
        latest_action = ""
        bill_with_latest_action = ""

        if total_bills > 0:
            latest_bill = bills.filter(from_organization=chamber).latest("created_at").created_at
            bill_with_latest_action = bills.filter(from_organization=chamber).latest("actions__date")
            # In case bills don't have actions
            if bill_with_latest_action.actions.count() > 0:
                latest_action = bill_with_latest_action.actions.latest("date")

        total_bills_per_session[chamber_name].append({
            "chamber": chamber,
            "total_bills": total_bills,
            "latest_bill": latest_bill,
            "bill_with_latest_action": bill_with_latest_action,
            "latest_action": latest_action}
        )
    return total_bills_per_session


def average_number_data(bills, chambers):
    average_num_data = defaultdict(list)

    for chamber in chambers:
        chamber_name = chamber.name.lower()
        total_sponsorships_per_bill = []
        total_actions_per_bill = []
        total_votes_per_bill = []

        average_sponsors_per_bill = 0
        average_actions_per_bill = 0
        average_votes_per_bill = 0

        for bill in bills.filter(from_organization=chamber):
            total_sponsorships_per_bill.append(bill.sponsorships.count())
            total_actions_per_bill.append(bill.actions.count())
            total_votes_per_bill.append(bill.votes.count())

        average_sponsors_per_bill = round(mean(total_sponsorships_per_bill))
        average_actions_per_bill = round(mean(total_actions_per_bill))
        average_votes_per_bill = round(mean(total_votes_per_bill))

        average_num_data[chamber_name].append({
            "chamber": chamber_name,
            "average_sponsors_per_bill": average_sponsors_per_bill,
            "average_actions_per_bill": average_actions_per_bill,
            "average_votes_per_bill": average_votes_per_bill}
        )
    return average_num_data


def no_sources(bills, chambers):
    no_sources_data = defaultdict(list)
    for chamber in chambers:
        chamber_name = chamber.name.lower()
        total_bills_no_sources = bills.filter(from_organization=chamber, sources=None).count()
        total_votes_no_sources = bills.filter(from_organization=chamber, votes__sources=None).count()
        no_sources_data[chamber_name].append({
            "chamber": chamber,
            "total_bills_no_sources": total_bills_no_sources,
            "total_votes_no_sources": total_votes_no_sources}
        )
    return no_sources_data


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
                print(session)
                bills_per_session = total_bills_per_session(bills, chambers)
                average_num_data = average_number_data(bills, chambers)
                no_sources_data = no_sources(bills, chambers)
                print("------")
