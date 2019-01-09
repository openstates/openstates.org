from .common import abbr_to_jid
from opencivicdata.core.models import Organization


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
    legislature = Organization.objects.select_related('jurisdiction').get(
        classification="legislature", jurisdiction_id=abbr_to_jid(abbr)
    )
    return legislature
