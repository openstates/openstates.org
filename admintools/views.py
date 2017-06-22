from django.shortcuts import render
from pupa.models import RunPlan
from opencivicdata.core.models import (Jurisdiction, Person, Organization,
                                       Membership)
from opencivicdata.legislative.models import Bill, VoteEvent
from admintools.issues import IssueType
from admintools.models import DataQualityIssue
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from collections import defaultdict
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q

# Basic Classes with their Identifiers.
upstream = {'person': Person,
            'organization': Organization,
            'membership': Membership,
            'bill': Bill,
            'voteevent': VoteEvent}


def _get_run_status(jur_name):
    runs = RunPlan.objects.filter(jurisdiction=jur_name).order_by('-end_time')
    latest_date = runs.first().end_time.date()
    status = 0
    for run in runs:
        if run.success:
            break
        else:
            status += 1
    return {'count': None if status == 1 else status, 'date': latest_date}


# Status Page
def overview(request):
    rows = {}
    all_counts = DataQualityIssue.objects.values('jurisdiction', 'issue',
                                                 'alert').annotate(
                                                     Count('issue'))
    for counts in all_counts:
        jur = Jurisdiction.objects.filter(id=counts['jurisdiction']).first()
        counts['jurisdiction'] = jur.name
        rows.setdefault(counts['jurisdiction'], {}).setdefault(
            counts['issue'].split('-')[0], {})
        rows[counts['jurisdiction']][counts['issue'].split('-')[0]][
            counts['alert']] = rows[counts['jurisdiction']][
                counts['issue'].split('-')[0]].get(
                    counts['alert'], 0) + counts['issue__count']

        if not rows[counts['jurisdiction']].get('run'):
            rows[counts['jurisdiction']]['run'] = _get_run_status(jur)

    # RunPlan For those who don't have any type of dataquality_issues
    rest_jurs = Jurisdiction.objects.exclude(name__in=rows.keys())
    for jur in rest_jurs:
        rows[jur.name] = {}
        rows[jur.name]['run'] = _get_run_status(jur)

    rows = sorted(rows.items())
    return render(request, 'admintools/index.html', {'rows': rows})


# Calculates all dataquality_issues in given jurisdiction
def _jur_dataquality_issues(jur_name):
    cards = defaultdict(dict)
    issues = IssueType.choices()
    for issue, description in issues:
        related_class = IssueType.class_for(issue)
        cards[related_class][issue] = {}
        issue_type = IssueType.class_for(issue) + '-' + issue
        alert = IssueType.level_for(issue)
        cards[related_class][issue]['alert'] = True if alert == 'error' \
            else False
        cards[related_class][issue]['description'] = description
        ct_obj = ContentType.objects.get_for_model(upstream[related_class])
        j = Jurisdiction.objects.filter(
            name__exact=jur_name, dataquality_issues__content_type=ct_obj,
            dataquality_issues__issue=issue_type).annotate(_issues=Count(
                'dataquality_issues'))
        cards[related_class][issue]['count'] = j[0]._issues if j else 0
    return dict(cards)


# Jurisdiction Specific Page
def jurisdiction_intro(request, jur_name):
    issues = _jur_dataquality_issues(jur_name)
    context = {'jur_name': jur_name, 'cards': issues}
    return render(request, 'admintools/jurisdiction_intro.html', context)


# Filter Results
def _filter_results(request):
    query = Q()
    if request.GET.get('person'):
        query = Q(name__istartswith=request.GET.get('person'))
    if request.GET.get('organization'):
        query &= Q(name__istartswith=request.GET.get('organization'))
    if request.GET.get('org_classification'):
        query &= Q(classification__istartswith=request.GET.get(
            'org_classification'))
    if request.GET.get('bill_identifier'):
        query &= Q(identifier__icontains=request.GET.get('bill_identifier'))
    if request.GET.get('bill_session'):
        query &= Q(legislative_session__name__icontains=request.GET.get(
            'bill_session'))
    if request.GET.get('voteevent_bill'):
        query &= Q(bill__identifier__icontains=request.GET.get(
            'voteevent_bill'))
    if request.GET.get('voteevent_org'):
        query &= Q(organization__name__icontains=request.GET.get(
            'voteevent_org'))
    if request.GET.get('membership'):
        query &= Q(person_name__istartswith=request.GET.get('membership'))
    if request.GET.get('membership_org'):
        query &= Q(organization__name__icontains=request.GET.get(
            'membership_org'))
    if request.GET.get('membership_id'):
        query &= Q(id=request.GET.get('membership_id'))
    return query


# Lists given issue(s) related objetcs
def list_issue_objects(request, jur_name, related_class, issue_slug):
    description = IssueType.description_for(issue_slug)
    issue = IssueType.class_for(issue_slug) + '-' + issue_slug
    objects_list = DataQualityIssue.objects.filter(
        jurisdiction__name__exact=jur_name,
        issue=issue).values_list('object_id', flat=True)
    cards = upstream[related_class].objects.filter(id__in=objects_list)
    if request.GET:
        cards = cards.filter(_filter_results(request))

    # pagination of results
    # order_by because of 'UnorderedObjectListWarning'
    paginator = Paginator(cards.order_by('id'), 20)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        objects = paginator.page(page)
    except(EmptyPage, InvalidPage):
        objects = paginator.page(1)

    # page_range to show at bottom of table
    index = objects.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 4 if index >= 4 else 0
    end_index = index + 4 if index <= max_index - 4 else max_index
    page_range = paginator.page_range[start_index:end_index]

    # url_slug used to address the Django-admin page
    if related_class in ['person', 'organization']:
        url_slug = 'core_' + related_class + '_change'
    elif related_class in ['bill', 'voteevent']:
        url_slug = 'legislative_' + related_class + '_change'
    else:
        url_slug = None

    context = {'jur_name': jur_name,
               'issue_slug': issue_slug,
               'objects': objects,
               'description': description,
               'page_range': page_range,
               'url_slug': url_slug,
               'related_class': related_class}
    return render(request, 'admintools/list_issues.html', context)
