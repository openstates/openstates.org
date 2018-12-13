from django.db.models import Min, Func, Max, OuterRef, Subquery
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from opencivicdata.core.models import Person
from opencivicdata.legislative.models import Bill, LegislativeSession, BillAction
from utils.common import abbr_to_jid
from utils.orgs import get_chambers_from_abbr
from utils.bills import fix_bill_id


class Unnest(Func):
    function = "UNNEST"


def bills(request, state):
    """
        form values:
            query
            chamber: lower|upper
            session
            status: passed-lower-chamber|passed-upper-chamber|signed
            sponsor (ocd-person ID)
            classification
            subjects
    """
    latest_actions = (
        BillAction.objects.filter(bill=OuterRef("pk"))
        .order_by("date")
        .values("description")[:1]
    )
    bills = (
        Bill.objects.all()
        .annotate(first_action_date=Min("actions__date"))
        .annotate(latest_action_date=Max("actions__date"))
        .annotate(latest_action_description=Subquery(latest_actions))
        .select_related("legislative_session", "legislative_session__jurisdiction")
        .prefetch_related("actions")
    )
    jid = abbr_to_jid(state)
    bills = bills.filter(legislative_session__jurisdiction_id=jid)

    # filter options
    chambers = get_chambers_from_abbr(state)
    chambers = {c.classification: c.name for c in chambers}
    sessions = LegislativeSession.objects.filter(jurisdiction_id=jid).order_by(
        "-start_date"
    )
    sponsors = Person.objects.filter(
        memberships__organization__jurisdiction_id=jid
    ).distinct()
    classifications = sorted(
        bills.annotate(type=Unnest("classification", distinct=True))
        .values_list("type", flat=True)
        .distinct()
    )
    subjects = sorted(
        bills.annotate(sub=Unnest("subject", distinct=True))
        .values_list("sub", flat=True)
        .distinct()
    )

    # query parameter filtering
    query = request.GET.get("query")
    chamber = request.GET.get("chamber")
    session = request.GET.get("session")
    sponsor = request.GET.get("sponsor")
    classification = request.GET.get("classification")
    q_subjects = request.GET.getlist("subjects")
    status = request.GET.getlist("status")

    form = {
        "query": query,
        "chamber": chamber,
        "session": session,
        "sponsor": sponsor,
        "classification": classification,
        "subjects": q_subjects,
        "status": status
    }

    if query:
        bills = bills.filter(title__icontains=query)
    if chamber:
        bills = bills.filter(from_organization__classification=chamber)
    if session:
        bills = bills.filter(legislative_session__identifier=session)
    if sponsor:
        bills = bills.filter(sponsorships__person_id=sponsor)
    if classification:
        bills = bills.filter(classification__contains=[classification])
    if q_subjects:
        bills = bills.filter(subject__overlap=q_subjects)
    if "passed-lower-chamber" in status:
        bills = bills.filter(actions__classification__contains=["passage"],
                             actions__organization__classification="lower")
    elif "passed-upper-chamber" in status:
        bills = bills.filter(actions__classification__contains=["passage"],
                             actions__organization__classification="upper")
    elif "signed" in status:
        bills = bills.filter(actions__classification__contains=["executive-signature"])

    # pagination
    bills = bills.order_by("-latest_action_date")
    page_num = int(request.GET.get("page", 1))
    paginator = Paginator(bills, 20)
    bills = paginator.page(page_num)

    return render(
        request,
        "public/views/bills.html",
        {
            "state": state,
            "state_nav": "bills",
            "bills": bills,
            "form": form,
            "chambers": chambers,
            "sessions": sessions,
            "sponsors": sponsors,
            "classifications": classifications,
            "subjects": subjects,
        },
    )


def bill(request, state, session, bill_id):
    jid = abbr_to_jid(state)
    identifier = fix_bill_id(bill_id)
    bill = get_object_or_404(
        Bill,
        legislative_session__jurisdiction_id=jid,
        legislative_session__identifier=session,
        identifier=identifier,
    )

    return render(
        request,
        "public/views/bill.html",
        {"state": state, "bill": bill, "state_nav": "bills"},
    )
