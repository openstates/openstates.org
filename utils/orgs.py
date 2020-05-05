from .common import abbr_to_jid, pretty_url
from openstates.data.models import Organization


def get_chambers_from_abbr(abbr):
    jid = abbr_to_jid(abbr)
    orgs = list(
        Organization.objects.filter(
            jurisdiction_id=jid, classification__in=["upper", "lower", "legislature"]
        )
    )
    if len(orgs) == 3:
        orgs = [org for org in orgs if org.classification != "legislature"]

    return orgs


def get_legislature_from_abbr(abbr):
    legislature = Organization.objects.select_related("jurisdiction").get(
        classification="legislature", jurisdiction_id=abbr_to_jid(abbr)
    )
    return legislature


def org_as_dict(org):
    return {
        "id": org.id,
        "name": org.name,
        "chamber": org.parent.classification,
        "pretty_url": pretty_url(org),
        "member_count": org.member_count,
    }
