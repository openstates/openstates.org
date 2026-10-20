import us
import uuid
import base62
from django.utils.text import slugify
from django.db.models import Count
from openstates.data.models import Person
from openstates.data.models import Bill, VoteEvent, LegislativeSession

# Metadata for states that are available in the platform
states = sorted(us.STATES + [us.states.PR, us.states.DC], key=lambda s: s.name)


def jid_to_abbr(j):
    return j.split(":")[-1].split("/")[0]


def abbr_to_jid(abbr):
    abbr = abbr.lower()
    if abbr == "us":
        return "ocd-jurisdiction/country:us/government"
    elif abbr == "dc":
        return "ocd-jurisdiction/country:us/district:dc/government"
    elif abbr == "pr":
        return "ocd-jurisdiction/country:us/territory:pr/government"
    else:
        return f"ocd-jurisdiction/country:us/state:{abbr}/government"


def encode_uuid(id):
    uuid_portion = str(id).split("/")[1]
    as_int = uuid.UUID(uuid_portion).int
    return base62.encode(as_int)


def decode_uuid(id, type="person"):
    decoded = uuid.UUID(int=base62.decode(id))
    return f"ocd-{type}/{decoded}"


def pretty_url(obj):
    if isinstance(obj, Person):
        return f"/person/{slugify(obj.name)}-{encode_uuid(obj.id)}/"
    elif isinstance(obj, dict) and obj["id"].startswith("ocd-person"):
        return f"/person/{slugify(obj['name'])}-{encode_uuid(obj['id'])}/"
    elif isinstance(obj, Bill):
        state = jid_to_abbr(obj.legislative_session.jurisdiction_id)
        identifier = obj.identifier.replace(" ", "")
        return f"/{state}/bills/{obj.legislative_session.identifier}/{identifier}/"
    elif isinstance(obj, VoteEvent):
        vote_id = obj.id.split("/")[1]
        return f"/vote/{vote_id}/"
    else:
        raise NotImplementedError(obj)


def sessions_with_bills(jid, active_only=False):
    if active_only:
        return (
            LegislativeSession.objects.filter(jurisdiction_id=jid)
            .annotate(bill_count=Count("bills"))
            .filter(bill_count__gt=0)
            .filter(active=True)
            .order_by("-start_date", "-identifier")
        )
    else:
        return (
            LegislativeSession.objects.filter(jurisdiction_id=jid)
            .annotate(bill_count=Count("bills"))
            .filter(bill_count__gt=0)
            .order_by("-start_date", "-identifier")
        )
