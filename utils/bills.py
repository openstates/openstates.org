import re
from django.db.models import Min, Max, OuterRef, Subquery
from opencivicdata.legislative.models import Bill, BillAction
from .websearchquery import WebSearchQuery as SearchQuery
from .common import abbr_to_jid

# This function has to match openstates.transformers
_bill_id_re = re.compile(r"([A-Z]*)\s*0*([-\d]+)")
_mi_bill_id_re = re.compile(r"(SJR|HJR)\s*([A-Z]+)")


def fix_bill_id(bill_id):
    # special case for MI Joint Resolutions
    if _mi_bill_id_re.match(bill_id):
        return _mi_bill_id_re.sub(r"\1 \2", bill_id, 1).strip()
    return _bill_id_re.sub(r"\1 \2", bill_id, 1).strip()


def get_bills_with_action_annotation():
    """
    return Bill queryset that is already annotated with:
        first_action_date
        latest_action_date
        latest_action_description

    and legislative_session & jurisdiction in the select_related already
    """
    latest_actions = (
        BillAction.objects.filter(bill=OuterRef("pk"))
        .order_by("date")
        .values("description")[:1]
    )
    return (
        Bill.objects.all()
        .annotate(first_action_date=Min("actions__date"))
        .annotate(latest_action_date=Max("actions__date"))
        .annotate(latest_action_description=Subquery(latest_actions))
        .select_related("legislative_session", "legislative_session__jurisdiction")
        .prefetch_related("actions")
    )


def search_bills(
    *,
    bills=None,
    query=None,
    state=None,
    chamber=None,
    session=None,
    sponsor=None,
    classification=None,
    subjects=None,
    status=None
):
    if not bills:
        bills = Bill.objects.all().select_related(
            "legislative_session", "legislative_session__jurisdiction", "billstatus"
        )
    if state:
        jid = abbr_to_jid(state.lower())
        bills = bills.filter(legislative_session__jurisdiction_id=jid)
    if query:
        if re.match(r"\w{1,3}\s*\d{1,5}", query):
            bills = bills.filter(identifier__iexact=fix_bill_id(query))
        else:
            bills = bills.filter(
                searchable__search_vector=SearchQuery(
                    query, search_type="web", config="english"
                )
            )
    if chamber:
        bills = bills.filter(from_organization__classification=chamber)
    if session:
        bills = bills.filter(legislative_session__identifier=session)
    if sponsor:
        bills = bills.filter(sponsorships__person_id=sponsor)
    if classification:
        bills = bills.filter(classification__contains=[classification])
    if subjects:
        bills = bills.filter(subject__overlap=subjects)

    if not status:
        status = []
    if "passed-lower-chamber" in status:
        bills = bills.filter(
            actions__classification__contains=["passage"],
            actions__organization__classification="lower",
        )
    elif "passed-upper-chamber" in status:
        bills = bills.filter(
            actions__classification__contains=["passage"],
            actions__organization__classification="upper",
        )
    elif "signed" in status:
        bills = bills.filter(actions__classification__contains=["executive-signature"])

    return bills
