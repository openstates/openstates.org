import os
import csv
from django.core.management.base import BaseCommand
from django.db.models import F
from opencivicdata.legislative.models import (
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


def export_csv(filename, data):
    if not data:
        return
    headers = data[0].keys()
    with open(filename, "w") as f:
        of = csv.DictWriter(f, headers)
        of.writeheader()
        of.writerows(data)


def export_session(state, session):
    sobj = LegislativeSession.objects.get(
        jurisdiction_id=abbr_to_jid(state), identifier=session
    )
    bills = Bill.objects.filter(legislative_session=sobj).values(
        "id",
        "identifier",
        "title",
        "classification",
        "subject",
        session_identifier=F("legislative_session__identifier"),
        jurisdiction=F("legislative_session__jurisdiction__name"),
        organization_classification=F("from_organization__classification"),
    )
    os.makedirs(f"{state}/{session}")
    export_csv(f"{state}/{session}/{state}_{session}_bills.csv", bills)

    for Model, fname in (
        (BillAbstract, "bill_abstracts"),
        (BillTitle, "bill_titles"),
        (BillIdentifier, "bill_identifiers"),
        (BillAction, "bill_actions"),
        (BillSource, "bill_sources"),
        (RelatedBill, "bill_related_bills"),
        (BillSponsorship, "bill_sponsorships"),
        (BillDocument, "bill_documents"),
        (BillVersion, "bill_versions"),
    ):
        subobjs = Model.objects.filter(bill__legislative_session=sobj).values()
        export_csv(f"{state}/{session}/{state}_{session}_{fname}.csv", subobjs)

    subobjs = BillDocumentLink.objects.filter(
        document__bill__legislative_session=sobj
    ).values()
    export_csv(f"{state}/{session}/{state}_{session}_bill_document_links.csv", subobjs)
    subobjs = BillVersionLink.objects.filter(
        version__bill__legislative_session=sobj
    ).values()
    export_csv(f"{state}/{session}/{state}_{session}_bill_version_links.csv", subobjs)

    # TODO: BillActionRelatedEntity

    # Votes
    votes = VoteEvent.objects.filter(legislative_session=sobj).values(
        "id",
        "identifier",
        "motion_text",
        "motion_classification",
        "start_date",
        "result",
        "organization_id",
        "bill_id",
        "bill_action_id",
        jurisdiction=F("legislative_session__jurisdiction__name"),
        session_identifier=F("legislative_session__identifier"),
    )
    export_csv(f"{state}/{session}/{state}_{session}_votes.csv", votes)
    for Model, fname in (
        (PersonVote, "vote_people"),
        (VoteCount, "vote_counts"),
        (VoteSource, "vote_sources"),
    ):
        subobjs = Model.objects.filter(vote_event__legislative_session=sobj).values()
        export_csv(f"{state}/{session}/{state}_{session}_{fname}.csv", subobjs)


class Command(BaseCommand):
    help = "export data as CSV"

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("sessions", nargs="*")
        parser.add_argument("--all", action="store_true")

    def handle(self, *args, **options):
        state = options["state"]
        sessions = [
            s.identifier
            for s in LegislativeSession.objects.filter(
                jurisdiction_id=abbr_to_jid(state)
            )
        ]
        if options["all"]:
            options["sessions"] = sessions
        if not options["sessions"]:
            print("available sessions:")
            for session in sessions:
                print("    ", session)
        else:
            for session in options["sessions"]:
                if session in sessions:
                    export_session(state, session)
