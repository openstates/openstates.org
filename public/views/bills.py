from collections import defaultdict
from django.core.paginator import Paginator
from django.db.models import Func, Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, reverse, redirect
from django.utils.feedgenerator import Rss201rev2Feed
from django.views import View
from opencivicdata.core.models import Membership
from opencivicdata.legislative.models import Bill, BillActionRelatedEntity, VoteEvent
from utils.common import abbr_to_jid, jid_to_abbr, pretty_url, sessions_with_bills
from utils.orgs import get_chambers_from_abbr
from utils.bills import fix_bill_id
from .fallback import fallback
from ..models import PersonProxy


class Unnest(Func):
    function = "UNNEST"


class BillList(View):
    def get_filter_options(self, state):
        options = {}
        jid = abbr_to_jid(state)
        bills = Bill.objects.all().filter(legislative_session__jurisdiction_id=jid)
        chambers = get_chambers_from_abbr(state)
        options["chambers"] = {c.classification: c.name for c in chambers}
        options["sessions"] = sessions_with_bills(jid)
        options["sponsors"] = PersonProxy.objects.filter(
            memberships__organization__jurisdiction_id=jid
        ).distinct()
        options["classifications"] = sorted(
            bills.annotate(type=Unnest("classification", distinct=True))
            .values_list("type", flat=True)
            .distinct()
        )
        options["subjects"] = sorted(
            bills.annotate(sub=Unnest("subject", distinct=True))
            .values_list("sub", flat=True)
            .distinct()
        )
        return options

    def get_bills(self, request, state):
        jid = abbr_to_jid(state)
        bills = Bill.objects.all().select_related(
            "legislative_session", "legislative_session__jurisdiction", "billstatus"
        )
        bills = bills.filter(legislative_session__jurisdiction_id=jid)

        # query parameter filtering
        query = request.GET.get("query", "")
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
            bills = bills.filter(
                actions__classification__contains=["executive-signature"]
            )

        bills = bills.order_by("-billstatus__latest_action_date")

        return bills, form

    def get(self, request, state):
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
        bills, form = self.get_bills(request, state)

        # pagination
        page_num = int(request.GET.get("page", 1))
        paginator = Paginator(bills, 20)
        bills = paginator.page(page_num)

        context = {
            "state": state,
            "state_nav": "bills",
            "bills": paginator.page(page_num),
            "form": form,
        }
        context.update(self.get_filter_options(state))

        return render(request, "public/views/bills.html", context)


class BillListFeed(BillList):
    def get(self, request, state):
        bills, form = self.get_bills(request, state)
        host = request.get_host()
        link = "https://{}{}?{}".format(
            host,
            reverse("bills", kwargs={"state": state}),
            request.META["QUERY_STRING"],
        )
        feed_url = "https://%s%s?%s" % (
            host,
            reverse("bills_feed", kwargs={"state": state}),
            request.META["QUERY_STRING"],
        )
        description = f"{state.upper()} Bills"
        if form["session"]:
            description += " ({form['session']})"
        # TODO: improve RSS description
        feed = Rss201rev2Feed(
            title=description,
            link=link,
            feed_url=feed_url,
            ttl=360,
            description=description,
        )
        for item in bills[:100]:
            link = "https://{}{}".format(host, pretty_url(item))
            feed.add_item(
                title=item.identifier,
                link=link,
                unique_id=link,
                description=f"""{item.title}<br />
                          Latest Action: {item.latest_action_description}
                          <i>{item.latest_action_date}</i>""",
            )
        return HttpResponse(feed.writeString("utf-8"), content_type="application/xml")


def _document_sort_key(doc):
    ordering = ["text/html", "application/pdf"]
    if doc.media_type in ordering:
        return (ordering.index(doc.media_type), doc.media_type)
    return (100, doc.media_type)


def compute_bill_stages(actions, first_chamber, second_chamber):
    """
        return a structure with four entries like
            stage: Introduced
            text: Introduced in House
            date: 2018-01-01
        or, if empty
            stage: Senate
            text: None
            date: None
    """
    stages = [
        {"stage": "Introduced", "text": None, "date": None},
        {"stage": first_chamber, "text": None, "date": None},
        {"stage": second_chamber, "text": None, "date": None},
        {"stage": "Governor", "text": None, "date": None},
    ]

    for action in actions:
        if "introduction" in action.classification and stages[0]["date"] is None:
            stages[0]["date"] = action.date
            stages[0]["text"] = f"Introduced in {first_chamber}"
        elif "passage" in action.classification:
            if action.organization.name == first_chamber:
                stages[1]["date"] = action.date
                stages[1]["text"] = f"Passed {first_chamber}"
            elif action.organization.name == second_chamber:
                stages[2]["date"] = action.date
                stages[2]["text"] = f"Passed {second_chamber}"
        elif "executive-signed" in action.classification and stages[3]["date"] is None:
            stages[3]["date"] = action.date
            stages[3]["text"] = "Signed by Governor"
        elif "became-law" in action.classification and stages[3]["date"] is None:
            stages[3]["date"] = action.date
            stages[3]["text"] = "Became Law"
        # TODO: veto, failure, etc?

    # if we're unicameral, remove second stage and make first stage name simpler
    if second_chamber is None:
        stages.pop(2)
        stages[1]["stage"] = "Legislature"

    return stages


def bill(request, state, session, bill_id):
    # canonicalize without space
    if " " in bill_id:
        return redirect(
            "bill", state, session, bill_id.replace(" ", ""), permanent=True
        )

    jid = abbr_to_jid(state)
    identifier = fix_bill_id(bill_id)

    try:
        bill = Bill.objects.select_related(
            "legislative_session",
            "legislative_session__jurisdiction",
            "from_organization",
        ).get(
            legislative_session__jurisdiction_id=jid,
            legislative_session__identifier=session,
            identifier=identifier,
        )
    except Bill.DoesNotExist:
        # try to find the asset in S3
        request.path = request.path.replace(bill_id, identifier)
        return fallback(request)

    # sponsorships, attach people manually
    sponsorships = list(bill.sponsorships.all())
    sponsor_people = {
        p.id: p
        for p in PersonProxy.objects.filter(
            id__in=[s.person_id for s in sponsorships if s.person_id]
        ).prefetch_related(
            "memberships", "memberships__organization", "memberships__post"
        )
    }
    for s in sponsorships:
        s.person = sponsor_people.get(s.person_id)

    related_entities = Prefetch(
        "related_entities",
        BillActionRelatedEntity.objects.all().select_related("person", "organization"),
    )
    actions = list(
        bill.actions.all()
        .select_related("organization")
        .prefetch_related(related_entities)
    )
    votes = list(
        bill.votes.all().select_related("organization")
    )  # .prefetch_related('counts')

    # stage calculation
    # get other chamber name
    chambers = {c.classification: c.name for c in get_chambers_from_abbr(state)}
    second_chamber = None
    if len(chambers) > 1:
        second_chamber = {"upper": chambers["lower"], "lower": chambers["upper"]}[
            bill.from_organization.classification
        ]
    stages = compute_bill_stages(actions, bill.from_organization.name, second_chamber)

    versions = list(bill.versions.order_by("-date").prefetch_related("links"))
    documents = list(bill.documents.order_by("-date").prefetch_related("links"))
    try:
        sorted_links = sorted(versions[0].links.all(), key=_document_sort_key)
        read_link = sorted_links[0].url
    except IndexError:
        read_link = None

    return render(
        request,
        "public/views/bill.html",
        {
            "state": state,
            "state_nav": "bills",
            "unicameral": state in ("dc", "ne"),
            "bill": bill,
            "sponsorships": sponsorships,
            "actions": actions,
            "stages": stages,
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

    # add percentages to vote_counts
    total = sum(vc.value for vc in vote_counts)
    for vc in vote_counts:
        vc.percent = vc.value / total * 100

    # aggregate voter ids into one query
    voter_ids_to_query = [pv.voter_id for pv in person_votes if pv.voter_id]
    voter_parties = defaultdict(list)
    # party -> option -> value
    party_votes = defaultdict(lambda: defaultdict(int))
    for membership in Membership.objects.filter(
        person_id__in=voter_ids_to_query, organization__classification="party"
    ).select_related("organization"):
        voter_parties[membership.person_id].append(membership.organization.name)

    # attach party to people & calculate party-option crosstab
    for pv in person_votes:
        # combine other options
        if pv.option not in ('yes', 'no'):
            option = 'other'
        else:
            option = pv.option

        if pv.voter_id:
            pv.party = voter_parties[pv.voter_id][0]
            party_votes[pv.party][option] += 1
        else:
            party_votes['Unknown'][option] += 1

    # only show party breakdown if most people are matched
    if len(voter_parties) / len(person_votes) < 0.8:
        party_votes = None
    else:
        party_votes = sorted(dict(party_votes).items())

    return render(
        request,
        "public/views/vote.html",
        {
            "state": state,
            "state_nav": "bills",
            "vote": vote,
            "vote_counts": vote_counts,
            "person_votes": person_votes,
            "party_votes": party_votes,
        },
    )
