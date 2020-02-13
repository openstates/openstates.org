import re
from opencivicdata.legislative.models import Bill
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
    if bills is None:
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
