from django.db.models import Min, Func, Max, OuterRef, Subquery, Prefetch
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from opencivicdata.core.models import Person
from opencivicdata.legislative.models import (
    Bill,
    LegislativeSession,
    BillAction,
    BillActionRelatedEntity,
    VoteEvent,
)
from utils.common import abbr_to_jid, jid_to_abbr
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
        "status": status,
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
        Bill.objects.all().select_related(
            "legislative_session",
            "legislative_session__jurisdiction",
            "from_organization",
        ),
        legislative_session__jurisdiction_id=jid,
        legislative_session__identifier=session,
        identifier=identifier,
    )

    sponsorships = list(bill.sponsorships.all().select_related("person"))
    related_entities = Prefetch(
        "related_entities",
        BillActionRelatedEntity.objects.all().select_related("person", "organization"),
    )
    actions = list(
        bill.actions.all()
        .select_related("organization")
        .prefetch_related(related_entities)
    )
    votes = list(bill.votes.all())  # .prefetch_related('counts')
    versions = list(bill.versions.all().prefetch_related("links"))
    documents = list(bill.documents.all().prefetch_related("links"))
    try:
        read_link = versions[0].links.all()[0].url
    except IndexError:
        read_link = None

    return render(
        request,
        "public/views/bill.html",
        {
            "state": state,
            "state_nav": "bills",
            "bill": bill,
            "sponsorships": sponsorships,
            "actions": actions,
            "votes": votes,
            "versions": versions,
            "documents": documents,
            "read_link": read_link,
        },
    )


def _vote_sort_key(v):
    if v.option == "yes":
        return (1, v.option)
    elif v.option == "no":
        return (2, v.option)
    else:
        return (3, v.option)


def vote(request, vote_id):
    vote = get_object_or_404(
        VoteEvent.objects.all().select_related(
            "organization",
            "legislative_session",
            "bill",
            "bill__legislative_session",
            "bill__from_organization",
            "bill__legislative_session__jurisdiction",
        ),
        pk="ocd-vote/" + vote_id,
    )
    state = jid_to_abbr(vote.organization.jurisdiction_id)
    vote_counts = sorted(vote.counts.all(), key=_vote_sort_key)
    person_votes = sorted(vote.votes.all().select_related("voter"), key=_vote_sort_key)

    return render(
        request,
        "public/views/vote.html",
        {
            "state": state,
            "state_nav": "bills",
            "vote": vote,
            "vote_counts": vote_counts,
            "person_votes": person_votes,
        },
    )
