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
from ...models import DataExport
from utils.common import abbr_to_jid



def get_available_sessions(state):
    return sorted(
        s.identifier
        for s in LegislativeSession.objects.filter(jurisdiction_id=abbr_to_jid(state))
    )

class Command(BaseCommand):
    help = "export data quality as a json"

    def add_arguments(self, parser):
        parser.add_argument("state")
        # parser.add_argument("sessions", nargs="*")
        # parser.add_argument("--all-sessions", action="store_true")


    def handle(self, *args, **options):
        print("OH Hello")
        state = options["state"]
        sessions = get_available_sessions(state)
