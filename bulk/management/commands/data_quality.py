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
from django.db.models import F
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
    bills = Bill.objects.filter(legislative_session=sobj).prefetch_related("actions", "sponsorships")
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
    #         "votes",
    #         "votes__counts",
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
        print(chamber)
        # Average num sponsors per bill:
        # total_sponsorships_per_bill = bills.filter(from_organization=chamber)
        total_sponsorships_per_bill = []
        for bill in bills.filter(from_organization=chamber):
            total_sponsors = bill.sponsorships.count()
            total_sponsorships_per_bill.append(total_sponsors)
        if total_sponsorships_per_bill:
            print(round(mean(total_sponsorships_per_bill)))

        # Average num actions per bill:

        # Average num votes per bill:

    return average_num_data


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
                print("------")
