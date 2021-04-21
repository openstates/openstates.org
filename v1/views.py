import pytz
import datetime
import functools
from django.http import JsonResponse
from django.db.models import Max, Q, Prefetch
from django.shortcuts import get_object_or_404
from openstates.data.models import (
    Bill,
    LegislativeSession,
    Jurisdiction,
    Person,
    Post,
    Organization,
)
from .utils import v1_metadata, convert_post, convert_legislator, convert_bill
from utils.common import jid_to_abbr, abbr_to_jid
from utils.geo import coords_to_divisions
from utils.bills import search_bills
from profiles.verifier import verify_request


def api_method(view_func):
    """ check API key, log, and wrap JSONP response """

    @functools.wraps(view_func)
    def new_view(request, *args, **kwargs):
        error = verify_request(request, "v1")
        if error:
            return error
        resp = view_func(request, *args, **kwargs)
        callback = request.GET.get("callback")
        if callback:
            resp.content = bytes(callback, "utf8") + b"(" + resp.content + b")"
        return resp

    return new_view


def jurisdictions_qs():
    return (
        Jurisdiction.objects.filter(classification="state")
        .annotate(latest_run=Max("runs__start_time"))
        .prefetch_related(
            "legislative_sessions",
            Prefetch(
                "organizations",
                queryset=Organization.objects.filter(
                    classification__in=("upper", "lower", "legislature")
                ).prefetch_related("posts"),
                to_attr="chambers",
            ),
        )
    )


def bill_qs(include_votes):
    qs = Bill.objects.select_related(
        "legislative_session__jurisdiction", "from_organization"
    ).prefetch_related(
        "documents__links",
        "versions__links",
        "actions__organization",
        "abstracts",
        "sources",
        "sponsorships",
        "other_titles",
        "legacy_mapping",
    )
    if include_votes:
        qs = qs.prefetch_related(
            "votes__counts",
            "votes__votes",
            "votes__sources",
            "votes__votes__voter",
            "votes__legislative_session",
            "votes__organization",
        )
    return qs


def person_qs():
    return Person.objects.prefetch_related(
        "identifiers",
        "memberships__organization",
        "memberships__post",
        "contact_details",
        "links",
        "sources",
    )


@api_method
def state_metadata(request, abbr):
    jid = abbr_to_jid(abbr.lower())
    jurisdiction = get_object_or_404(jurisdictions_qs(), pk=jid)
    return JsonResponse(v1_metadata(abbr.lower(), jurisdiction))


@api_method
def all_metadata(request):
    return JsonResponse(
        [v1_metadata(jid_to_abbr(j.id), j) for j in jurisdictions_qs()], safe=False
    )


@api_method
def legislator_detail(request, id):
    person = get_object_or_404(
        person_qs(), identifiers__scheme="legacy_openstates", identifiers__identifier=id
    )
    return JsonResponse(convert_legislator(person))


@api_method
def legislator_list(request, geo=False):
    abbr = request.GET.get("state")
    chamber = request.GET.get("chamber")
    district = request.GET.get("district")

    today = datetime.date.today().isoformat()
    filter_params = [
        Q(memberships__start_date="") | Q(memberships__start_date__lte=today),
        Q(memberships__end_date="") | Q(memberships__end_date__gte=today),
    ]

    if geo:
        latitude = request.GET.get("lat")
        longitude = request.GET.get("long")

        if not latitude or not longitude:
            return JsonResponse(
                "Bad Request: must include lat & long", status=400, safe=False
            )
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return JsonResponse("Bad Request: invalid lat, lon", status=400, safe=False)

        divisions = coords_to_divisions(latitude, longitude)
        filter_params.append(Q(memberships__post__division__id__in=divisions))

    if abbr:
        jid = abbr_to_jid(abbr)
        filter_params.append(Q(memberships__organization__jurisdiction_id=jid))
    if chamber:
        filter_params.append(Q(memberships__organization__classification=chamber))
    if district:
        filter_params.append(Q(memberships__post__label=district))

    people = person_qs().filter(*filter_params).distinct()

    return JsonResponse([convert_legislator(leg) for leg in people], safe=False)


@api_method
def district_list(request, abbr, chamber=None):
    jid = abbr_to_jid(abbr)
    if chamber is None:
        posts = Post.objects.filter(
            organization__jurisdiction_id=jid,
            organization__classification__in=("upper", "lower", "legislature"),
        )
    else:
        posts = Post.objects.filter(
            organization__jurisdiction_id=jid, organization__classification=chamber
        )

    posts = posts.select_related("organization")

    return JsonResponse([convert_post(p) for p in posts], safe=False)


@api_method
def bill_detail(
    request, abbr=None, session=None, bill_id=None, chamber=None, billy_bill_id=None
):
    if abbr:
        jid = abbr_to_jid(abbr)
        params = {
            "legislative_session__jurisdiction_id": jid,
            "legislative_session__identifier": session,
            "identifier": bill_id,
        }
    elif billy_bill_id:
        params = {"legacy_mapping__legacy_id": billy_bill_id}

    if chamber:
        if abbr in ("ne", "dc") and chamber == "upper":
            chamber = "legislature"
        params["from_organization__classification"] = chamber

    bills = bill_qs(include_votes=True)
    bill = get_object_or_404(bills, **params)
    return JsonResponse(convert_bill(bill, include_votes=True))


@api_method
def bill_list(request):
    state = request.GET.get("state")
    chamber = request.GET.get("chamber")
    bill_id = request.GET.get("bill_id")
    query = request.GET.get("q")
    search_window = request.GET.get("search_window", "all")
    updated_since = request.GET.get("updated_since")
    sort = request.GET.get("sort", "last")

    too_big = True
    bills = bill_qs(include_votes=False)
    if state in ("ne", "dc") and chamber == "upper":
        chamber = "legislature"
    # v1 sorts by its own options
    bills = search_bills(
        bills=bills, state=state, chamber=chamber, query=query, sort=None
    )
    if query:
        too_big = False
    if updated_since:
        updated_since = pytz.utc.localize(
            datetime.datetime.strptime(updated_since[:10], "%Y-%m-%d")
        )
        bills = bills.filter(updated_at__gt=updated_since)
        too_big = False
    if bill_id:
        bills = bills.filter(identifier=bill_id)
        too_big = False

    # search_window only ever really worked w/ state- and judging by analytics that's how
    # it was used in every case
    if state:
        if search_window == "session" or search_window == "term":
            latest_session = (
                LegislativeSession.objects.filter(
                    jurisdiction_id=abbr_to_jid(state.lower())
                )
                .order_by("-start_date")
                .values_list("identifier", flat=True)[0]
            )
            bills = bills.filter(legislative_session__identifier=latest_session)
            too_big = False
        elif search_window.startswith("session:"):
            bills = bills.filter(
                legislative_session__identifier=search_window.split("session:")[1]
            )
            too_big = False
        elif search_window != "all":
            return JsonResponse(
                'invalid search_window. valid choices are "term", "session", "all"',
                status=400,
                safe=False,
            )

    # first, last, created
    if sort == "created_at":
        bills = bills.order_by("-created_at")
    elif sort == "updated_at":
        bills = bills.order_by("-updated_at")
    else:
        bills = bills.order_by("-latest_action_date")

    # pagination
    page = request.GET.get("page")
    per_page = request.GET.get("per_page")
    if page and not per_page:
        per_page = 50
    if per_page and not page:
        page = 1

    if page and int(page) > 0:
        page = int(page)
        per_page = int(per_page)
        start = per_page * (page - 1)
        end = start + per_page
        bills = bills[start:end]
        too_big = per_page > 100
    elif too_big or bills.count() > 200:
        return JsonResponse(
            "Bad Request: request too large, try narrowing your search by "
            "adding more filters or using pagination.",
            status=400,
            safe=False,
        )

    return JsonResponse(
        [convert_bill(b, include_votes=False) for b in bills], safe=False
    )
