from django.core.paginator import Paginator
from django.db.models import Min, Func, Max, OuterRef, Subquery, Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.views import View
from opencivicdata.core.models import Person
from opencivicdata.legislative.models import (
    Bill,
    BillAction,
    BillActionRelatedEntity,
    VoteEvent,
)
from utils.common import abbr_to_jid, jid_to_abbr, pretty_url, sessions_with_bills
from utils.orgs import get_chambers_from_abbr
from utils.bills import fix_bill_id


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
        options["sponsors"] = Person.objects.filter(
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

        bills = bills.order_by("-latest_action_date")

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
