import csv
from django.core.management.base import BaseCommand
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
        "legislative_session__identifier",
        "legislative_session__jurisdiction__name",
        "identifier",
        "title",
        "from_organization__classification",
        "classification",
        "subject",
    )
    export_csv(f"{state}_{session}_bills.csv", bills)

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
        export_csv(f"{state}_{session}_{fname}.csv", subobjs)

    subobjs = BillDocumentLink.objects.filter(
        document__bill__legislative_session=sobj
    ).values()
    export_csv(f"{state}_{session}_bill_document_links.csv", subobjs)
    subobjs = BillVersionLink.objects.filter(
        version__bill__legislative_session=sobj
    ).values()
    export_csv(f"{state}_{session}_bill_version_links.csv", subobjs)

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
        "legislative_session__jurisdiction__name",
        "legislative_session__identifier",
        "bill_id",
        "bill_action_id",
    )
    export_csv(f"{state}_{session}_votes.csv", votes)
    for Model, fname in (
        (PersonVote, "vote_people"),
        (VoteCount, "vote_counts"),
    ):
        subobjs = Model.objects.filter(vote_event__legislative_session=sobj).values()
        export_csv(f"{state}_{session}_{fname}.csv", subobjs)


class Command(BaseCommand):
    help = "export data as CSV"

    def handle(self, *args, **options):
        export_session("nc", "2019")
