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
from openstates.metadata import STATES_BY_NAME
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
    Organization,
    PersonVote,
    VoteCount,
    VoteSource,
)
from ...models import DataExport
from utils.common import abbr_to_jid


def _str_uuid():
    return base62.encode(uuid.uuid4().int)


def export_csv(filename, data, zf):
    num = len(data)
    if not num:
        return
    headers = data[0].keys()

    with tempfile.NamedTemporaryFile("w") as f:
        print("writing", filename, num, "records")
        of = csv.DictWriter(f, headers)
        of.writeheader()
        of.writerows(data)
        f.flush()
        zf.write(f.name, filename)
    return num


def export_json(filename, data, zf):
    num = len(data)
    if not num:
        return

    with tempfile.NamedTemporaryFile("w") as f:
        print("writing", filename, num, "records")
        json.dump(data, f)
        f.flush()
        zf.write(f.name, filename)
    return num


def _docver_to_json(dv):
    return {
        "note": dv.note,
        "date": dv.date,
        "links": list(dv.links.values("url", "media_type")),
    }


def _vote_to_json(v):
    return {
        "identifier": v.identifier,
        "motion_text": v.motion_text,
        "motion_classification": v.motion_classification,
        "start_date": v.start_date,
        "result": v.result,
        "organization__classification": v.organization.classification,
        "counts": list(v.counts.values("option", "value")),
        "votes": list(v.votes.values("option", "voter_name")),
    }


def _bill_to_json(b):
    d = {
        "id": b.id,
        "legislative_session": b.legislative_session.identifier,
        "jurisdiction_name": b.legislative_session.jurisdiction.name,
        "identifier": b.identifier,
        "title": b.title,
        "chamber": b.from_organization.classification,
        "classification": b.classification,
        "subject": b.subject,
        "abstracts": list(b.abstracts.values("abstract", "note", "date")),
        "other_titles": list(b.other_titles.values("title", "note")),
        "other_identifiers": list(
            b.other_identifiers.values("note", "identifier", "scheme")
        ),
        "actions": list(
            b.actions.values(
                "organization__name", "description", "date", "classification", "order"
            )
        ),
        # TODO: action related entities
        "related_bills": list(b.related_bills.values("related_bill_id")),
        "sponsors": list(b.sponsorships.values("name", "primary", "classification")),
        "documents": [_docver_to_json(d) for d in b.documents.all()],
        "versions": [_docver_to_json(d) for d in b.versions.all()],
        "sources": list(b.sources.values("url")),
        # votes
        "votes": [_vote_to_json(v) for v in b.votes.all()],
    }
    try:
        d["raw_text"] = b.searchable.raw_text
        d["raw_text_url"] = b.searchable.version_link.url
    except Exception:
        pass
    return d


def export_session_csv(state, session):
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

    if not bills.count():
        print(f"no bills for {state} {session}")
        return
    random = _str_uuid()
    filename = f"/tmp/{state}_{session}_csv_{random}.zip"
    zf = zipfile.ZipFile(filename, "w")
    ts = datetime.datetime.utcnow()
    zf.writestr(
        "README",
        f"""Open States Data Export

State: {state}
Session: {session}
Generated At: {ts}
CSV Format Version: 2.1
""",
    )

    export_csv(f"{state}/{session}/{state}_{session}_bills.csv", bills, zf)

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
        export_csv(f"{state}/{session}/{state}_{session}_{fname}.csv", subobjs, zf)

    subobjs = BillDocumentLink.objects.filter(
        document__bill__legislative_session=sobj
    ).values()
    export_csv(
        f"{state}/{session}/{state}_{session}_bill_document_links.csv", subobjs, zf
    )
    subobjs = BillVersionLink.objects.filter(
        version__bill__legislative_session=sobj
    ).values()
    export_csv(
        f"{state}/{session}/{state}_{session}_bill_version_links.csv", subobjs, zf
    )

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
    export_csv(f"{state}/{session}/{state}_{session}_votes.csv", votes, zf)
    for Model, fname in (
        (PersonVote, "vote_people"),
        (VoteCount, "vote_counts"),
        (VoteSource, "vote_sources"),
    ):
        subobjs = Model.objects.filter(vote_event__legislative_session=sobj).values()
        export_csv(f"{state}/{session}/{state}_{session}_{fname}.csv", subobjs, zf)

    orgs = Organization.objects.filter(jurisdiction_id=sobj.jurisdiction_id).values()
    export_csv(f"{state}/{session}/{state}_{session}_organizations.csv", orgs, zf)

    return filename


def export_session_json(state, session):
    sobj = LegislativeSession.objects.get(
        jurisdiction_id=abbr_to_jid(state), identifier=session
    )
    bills = [
        _bill_to_json(b)
        for b in Bill.objects.filter(legislative_session=sobj)
        .select_related(
            "legislative_session",
            "legislative_session__jurisdiction",
            "from_organization",
            "searchable",
        )
        .prefetch_related(
            "abstracts",
            "other_titles",
            "other_identifiers",
            "actions",
            "related_bills",
            "sponsorships",
            "documents",
            "documents__links",
            "versions",
            "versions__links",
            "sources",
            "votes",
            "votes__counts",
            "votes__votes",
        )
    ]
    random = _str_uuid()
    filename = f"/tmp/{state}_{session}_json_{random}.zip"
    zf = zipfile.ZipFile(filename, "w")
    ts = datetime.datetime.utcnow()
    zf.writestr(
        "README",
        f"""Open States Data Export

State: {state}
Session: {session}
Generated At: {ts}
JSON Format Version: 1.0
""",
    )

    if export_json(f"{state}/{session}/{state}_{session}_bills.json", bills, zf):
        return filename


def upload_and_publish(state, session, filename, data_type):
    sobj = LegislativeSession.objects.get(
        jurisdiction_id=abbr_to_jid(state), identifier=session
    )
    s3 = boto3.client("s3")

    BULK_S3_BUCKET = "data.openstates.org"
    basename = os.path.basename(filename)
    s3_path = f"{data_type}/latest/"
    s3_url = f"https://{BULK_S3_BUCKET}/{s3_path}{basename}"

    s3.upload_file(
        filename, BULK_S3_BUCKET, s3_path + basename, ExtraArgs={"ACL": "public-read"}
    )
    print("uploaded", s3_url)
    obj, created = DataExport.objects.update_or_create(
        session=sobj, data_type=data_type, defaults=dict(url=s3_url),
    )


def get_available_sessions(state, updated_since=0):
    if updated_since:
        sessions = [
            b
            for b in Bill.objects.filter(
                legislative_session__jurisdiction_id=abbr_to_jid(state),
                updated_at__gte=datetime.datetime.now()
                - datetime.timedelta(days=updated_since),
            )
            .values_list("legislative_session__identifier", flat=True)
            .distinct()
        ]
    else:
        sessions = [
            s.identifier
            for s in LegislativeSession.objects.filter(
                jurisdiction_id=abbr_to_jid(state)
            )
        ]
    return sorted(sessions)


def export_data(state, session, data_type):
    if data_type == "csv":
        filename = export_session_csv(state, session)
    else:
        filename = export_session_json(state, session)
    if filename:
        upload_and_publish(state, session, filename, data_type)


def export_all_states(data_type, updates_since):
    for state in STATES_BY_NAME.values():
        for session in get_available_sessions(state.abbr, updates_since):
            export_data(state.abbr, session, data_type)


class Command(BaseCommand):
    help = "export data as CSV"

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("sessions", nargs="*")
        parser.add_argument("--all-sessions", action="store_true")
        parser.add_argument("--with-updates-days", type=int, default=0)  # days
        parser.add_argument("--format")

    def handle(self, *args, **options):
        data_type = options["format"]
        if data_type not in ("csv", "json"):
            raise ValueError("--format must be csv or json")
        state = options["state"]

        # special case
        if state == "all":
            export_all_states(data_type, options["with_updates_days"])
            return

        sessions = get_available_sessions(state, options["with_updates_days"])

        if options["all_sessions"]:
            options["sessions"] = sessions
        elif options["with_updates_days"]:
            print(
                f"{len(sessions)} sessions with updates in last {options['with_updates_days']} days"
            )
            options["sessions"] = sessions
        if not options["sessions"]:
            print("available sessions:")
            for session in sessions:
                print("    ", session)
        else:
            for session in options["sessions"]:
                if session in sessions:
                    export_data(state, session, data_type)
