import datetime
from django.http import JsonResponse
from django.db.models import Max, Min, Q, Prefetch
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import Point
from opencivicdata.legislative.models import Bill, LegislativeSession
from opencivicdata.core.models import Jurisdiction, Person, Post, Organization
from . import utils, static


# these are to mimic empty committee/event responses

def empty_list(request):
    return JsonResponse([], safe=False)


def item_404(request, id):
    return JsonResponse("Not Found", safe=False, status=404)


def jurisdictions_qs():
    return Jurisdiction.objects.all().annotate(
        latest_run=Max('runs__start_time')).prefetch_related(
            'legislative_sessions',
            Prefetch('organizations',
                     queryset=Organization.objects.filter(
                         classification__in=('upper', 'lower', 'legislature')
                     ).prefetch_related('posts'),
                     to_attr='chambers')
        )


def bill_qs():
    return Bill.objects.annotate(
        last_action=Max('actions__date'),
        first_action=Min('actions__date')
    ).select_related(
        'legislative_session__jurisdiction',
        'from_organization'
    ).prefetch_related(
        'documents__links', 'versions__links', 'actions__organization',
        'abstracts', 'sources', 'sponsorships', 'other_titles',
        'votes__counts', 'votes__votes', 'votes__sources',
        'votes__legislative_session', 'votes__organization',
    )


def person_qs():
    return Person.objects.prefetch_related(
        'identifiers', 'memberships__organization', 'memberships__post',
        'contact_details', 'links', 'sources',
    )


def state_metadata(request, abbr):
    jid = utils.abbr_to_jid(abbr)
    jurisdiction = jurisdictions_qs().get(pk=jid)
    return JsonResponse(utils.state_metadata(abbr, jurisdiction))


def all_metadata(request):
    return JsonResponse(
        [utils.state_metadata(utils.jid_to_abbr(j.id), j) for j in jurisdictions_qs()],
        safe=False
    )


def legislator_detail(request, id):
    person = get_object_or_404(person_qs(),
                               identifiers__scheme='legacy_openstates',
                               identifiers__identifier=id)
    return JsonResponse(
        utils.convert_legislator(person)
    )


def legislator_list(request, geo=False):
    abbr = request.GET.get('state')
    chamber = request.GET.get('chamber')
    district = request.GET.get('district')

    today = datetime.date.today().isoformat()
    filter_params = [Q(memberships__start_date='') |
                     Q(memberships__start_date__lte=today),
                     Q(memberships__end_date='') |
                     Q(memberships__end_date__gte=today),
                     ]

    if geo:
        latitude = request.GET.get('lat')
        longitude = request.GET.get('long')

        if not latitude or not longitude:
            return JsonResponse("Bad Request: must include lat & long",
                                status=400, safe=False)

        filter_params += [
            Q(memberships__post__division__geometries__boundary__shape__contains=(
                Point(float(longitude), float(latitude))
            )),
            Q(memberships__post__division__geometries__boundary__set__end_date=None) |
            Q(memberships__post__division__geometries__boundary__set__end_date__gt=today)
        ]

    if abbr:
        jid = utils.abbr_to_jid(abbr)
        filter_params.append(Q(memberships__organization__jurisdiction_id=jid))
    if chamber:
        filter_params.append(Q(memberships__organization__classification=chamber))
    if district:
        filter_params.append(Q(memberships__post__label=district))

    people = person_qs().filter(*filter_params).distinct()

    return JsonResponse(
        [utils.convert_legislator(l) for l in people],
        safe=False
    )


def district_list(request, abbr, chamber=None):
    jid = utils.abbr_to_jid(abbr)
    if chamber is None:
        posts = Post.objects.filter(
            organization__jurisdiction_id=jid,
            organization__classification__in=('upper', 'lower', 'legislature')
        )
    else:
        posts = Post.objects.filter(organization__jurisdiction_id=jid,
                                    organization__classification=chamber)

    posts = posts.select_related('organization')

    return JsonResponse(
        [utils.convert_post(p) for p in posts],
        safe=False
    )


def bill_detail(request,
                abbr=None, session=None, bill_id=None, chamber=None,
                billy_bill_id=None,
                ):
    if abbr:
        jid = utils.abbr_to_jid(abbr)
        params = {'legislative_session__jurisdiction_id': jid,
                  'legislative_session__identifier': session,
                  'identifier': bill_id}
    elif billy_bill_id:
        params = {'legacy_mapping__legacy_id': billy_bill_id}

    if chamber:
        if abbr in ('ne', 'dc') and chamber == 'upper':
            chamber = 'legislature'
        params['from_organization__classification'] = chamber

    bills = bill_qs()
    bill = get_object_or_404(bills, **params)
    return JsonResponse(utils.convert_bill(bill))


def bill_list(request):
    state = request.GET.get('state')
    chamber = request.GET.get('chamber')
    bill_id = request.GET.get('bill_id')
    query = request.GET.get('q')
    search_window = request.GET.get('search_window', 'all')
    updated_since = request.GET.get('updated_since')
    sort = request.GET.get('sort', 'last')

    bills = bill_qs()
    if state:
        jid = utils.abbr_to_jid(state)
        bills = bills.filter(legislative_session__jurisdiction_id=jid)
    if chamber:
        if state in ('ne', 'dc') and chamber == 'upper':
            chamber = 'legislature'
        bills = bills.filter(from_organization__classification=chamber)
    if query:
        bills = bills.filter(title__icontains=query)
    if updated_since:
        bills = bills.filter(updated_at__gt=updated_since)
    if bill_id:
        bills = bills.filter(identifier=bill_id)

    # search_window only ever really worked w/ state- and judging by analytics that's how
    # it was used in every case
    if state:
        if search_window == 'session':
            latest_session = LegislativeSession.objects.filter(
                jurisdiction_id=jid
            ).order_by('-start_date').values_list('identifier', flat=True)[0]
            bills = bills.filter(legislative_session__identifier=latest_session)
        elif search_window == 'term':
            latest_sessions = static.TERMS[state][-1]['sessions']
            bills = bills.filter(legislative_session__identifier__in=latest_sessions)
        elif search_window.startswith('session:'):
            bills = bills.filter(
                legislative_session__identifier=search_window.split('session:')[1]
            )
        elif search_window != 'all':
            raise ValueError('invalid search_window. valid choices are "term", "session", "all"')

    # first, last, created
    if sort == 'created_at':
        bills = bills.order_by('-created_at')
    elif sort == 'updated_at':
        bills = bills.order_by('-updated_at')
    else:
        bills = bills.order_by('-last_action')

    # pagination
    page = request.GET.get('page')
    per_page = request.GET.get('per_page')
    if page and not per_page:
        per_page = 50
    if per_page and not page:
        page = 1

    if page:
        page = int(page)
        per_page = int(per_page)
        start = per_page * (page - 1)
        end = start + per_page
        bills = bills[start:end]
    else:
        # limit response size
        if len(bills) > 1000:
            return JsonResponse("Bad Request: request too large, try narrowing your search by "
                                "adding more filters.", status=400, safe=False)

    return JsonResponse([utils.convert_bill(b) for b in bills], safe=False)
