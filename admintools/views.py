from django.shortcuts import render
from pupa.models import RunPlan
from opencivicdata.core.models import (Jurisdiction, Person, Organization,
                                       Membership)
from opencivicdata.legislative.models import (Bill, VoteEvent,
                                              LegislativeSession)
from admintools.issues import IssueType
from admintools.models import DataQualityIssue, IssueResolverPatch
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from collections import defaultdict
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db import transaction

# Basic Classes with their Identifiers.
upstream = {'person': Person,
            'organization': Organization,
            'membership': Membership,
            'bill': Bill,
            'voteevent': VoteEvent}


# get run status for a jurisdiction
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


def _get_pagination(objects_list, request):
    paginator = Paginator(objects_list, 20)
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

    return objects, page_range


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
    jur_id = Jurisdiction.objects.get(name__exact=jur_name).id
    bill_from_orgs_list = Bill.objects.filter(
        legislative_session__jurisdiction__name__exact=jur_name) \
        .values('from_organization__name').distinct()

    voteevent_orgs_list = VoteEvent.objects.filter(
        legislative_session__jurisdiction__name__exact=jur_name) \
        .values('organization__name').distinct()

    orgs_list = Organization.objects.filter(
        jurisdiction__name__exact=jur_name).values('classification').distinct()

    context = {'jur_name': jur_name,
               'jur_id': jur_id,
               'cards': issues,
               'bill_orgs': bill_from_orgs_list,
               'voteevent_orgs': voteevent_orgs_list,
               'orgs': orgs_list,
               }
    return render(request, 'admintools/jurisdiction_intro.html', context)


# Bills and VoteEvents related info for a session
def legislative_session_info(request, jur_name, identifier):
    session = LegislativeSession.objects.get(
        jurisdiction__name__exact=jur_name, identifier=identifier)

    bill_from_orgs_list = Bill.objects.filter(
        legislative_session__jurisdiction__name__exact=jur_name,
        legislative_session__identifier=identifier) \
        .values('from_organization__name').distinct()

    voteevent_orgs_list = VoteEvent.objects.filter(
        legislative_session__jurisdiction__name__exact=jur_name,
        legislative_session__identifier=identifier) \
        .values('organization__name').distinct()

    context = {
        'jur_name': jur_name,
        'session': session,
        'bill_orgs': bill_from_orgs_list,
        'voteevent_orgs': voteevent_orgs_list,
    }
    return render(request, 'admintools/legislative_session_info.html', context)


# Filter Results
def _filter_results(request):
    query = Q()
    if request.GET.get('person'):
        query = Q(name__icontains=request.GET.get('person'))
    if request.GET.get('organization'):
        query &= Q(name__icontains=request.GET.get('organization'))
    if request.GET.get('org_classification'):
        query &= Q(classification__icontains=request.GET.get(
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
        query &= Q(person_name__icontains=request.GET.get('membership'))
    if request.GET.get('membership_org'):
        query &= Q(organization__name__icontains=request.GET.get(
            'membership_org'))
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

    objects, page_range = _get_pagination(cards.order_by('id'), request)

    # url_slug used to address the Django-admin page
    if related_class in ['person', 'organization']:
        url_slug = 'core_' + related_class + '_change'
    elif related_class in ['bill', 'voteevent']:
        url_slug = 'legislative_' + related_class + '_change'
    else:
        # because we don't have membership objetcs listed on Django-admin panel
        # so redirect to related organization page
        url_slug = None

    context = {'jur_name': jur_name,
               'issue_slug': issue_slug,
               'objects': objects,
               'description': description,
               'page_range': page_range,
               'url_slug': url_slug,
               'related_class': related_class}
    return render(request, 'admintools/list_issues.html', context)


def _prepare_import(issue_slug, posted_data):
    if issue_slug == 'missing-photo':
        issue_items = dict((k, v) for k, v in posted_data.items()
                           if v and not k.startswith('csrf'))
    elif issue_slug in ['missing-phone', 'missing-email', 'missing-address']:
        issue_items = defaultdict(dict)
        count = 1
        for k, v in posted_data.items():
            if v and not k.startswith('csrf') and not k.startswith('note'):
                c = k.split("ocd-person/")
                # using custom hash because two legislators can have same Phone
                # numbers for eg, `State House Message Phone`
                hash_ = str(count) + '__@#$__' + v
                issue_items[hash_]['id'] = "ocd-person/" + c[1]
                issue_items[hash_]['code'] = c[0]
                count += 1
        for hash_, item in issue_items.items():
            issue_items[hash_]['note'] = posted_data['note_' + item['code']
                                                     + item['id']]
    else:
        raise ValueError("Person Issue Resolver needs update for new issue.")
    return issue_items


@transaction.atomic
def person_resolve_issues(request, issue_slug, jur_name):
    if request.method == 'POST':
        if issue_slug == 'missing-phone':
            category = 'voice'
        elif issue_slug == 'missing-photo':
            category = 'image'
        elif issue_slug in ['missing-email', 'missing-address']:
            category = issue_slug[8:]
        else:
            raise ValueError("Person Resolver needs update for new issue.")
        jur = Jurisdiction.objects.get(name__exact=jur_name)
        issue_items = _prepare_import(issue_slug, request.POST)
        for hash_, items in issue_items.items():
            if issue_slug != 'missing-photo':
                new_value = hash_.split('__@#$__')[1]
                p = Person.objects.get(id=items.get('id'))
                note = items.get('note')
            else:
                # hash_ == ocd id of person here.
                new_value = items
                p = Person.objects.get(id=hash_)
                note = ''
            patch = IssueResolverPatch.objects.create(
                content_object=p,
                jurisdiction=jur,
                status='unreviewed',
                new_value=new_value,
                note=note,
                category=category,
                alert='warning',
                applied_by='admin',
            )
            patch.save()
        messages.success(request, 'Successfully created {} {}(s) Admin '
                         'Patch(es)'.format(len(issue_items),
                                            IssueType.description_for(
                                              issue_slug)))
    return HttpResponseRedirect(reverse('list_issue_objects',
                                        args=(jur_name, 'person',
                                              issue_slug)))


def review_person_patches(request, jur_name):
    if request.method == 'POST':
        for k, v in request.POST.items():
            if not k.startswith('csrf'):
                # k = 'category__patch_id__object_id'
                # v = `status`
                c = k.split("__")
                if (c[0] == 'image' or c[0] == 'name') and v == 'approved':
                    try:
                        # mark alerady approved patch as deprecated (if any!)
                        approved_patch = IssueResolverPatch.objects.get(
                            object_id=c[2], category=c[0], status='approved')
                        approved_patch.status = 'deprecated'
                        approved_patch.save()
                    except IssueResolverPatch.DoesNotExist:
                        pass
                patch = IssueResolverPatch.objects.get(id=c[1])
                patch.status = v
                patch.save()
        if len(request.POST)-1:
            messages.success(request, 'Successfully updated status of {} '
                             'Patch(es)'.format(len(request.POST)-1))
    patches = IssueResolverPatch.objects \
        .filter(status='unreviewed', jurisdiction__name__exact=jur_name)
    category_search = False
    alert_search = False
    applied_by_search = False
    if request.GET.get('person'):
        person_ids = Person.objects.filter(
            memberships__organization__jurisdiction__name__exact=jur_name,
            name__icontains=request.GET.get('person'))
        patches = patches.filter(object_id__in=person_ids)
    if request.GET.get('category'):
        patches = patches.filter(category=request.GET.get('category'))
        category_search = request.GET.get('category')
    if request.GET.get('alert'):
        patches = patches.filter(alert=request.GET.get('alert'))
        alert_search = request.GET.get('alert')
    if request.GET.get('applied_by'):
        patches = patches.filter(applied_by=request.GET.get('applied_by'))
        applied_by_search = request.GET.get('applied_by')
    objects, page_range = _get_pagination(patches.order_by('id'), request)
    categories_ = sorted(dict(IssueResolverPatch._meta.get_field(
        'category').choices).items())
    alerts_ = sorted(dict(IssueResolverPatch._meta.get_field(
        'alert').choices).items())
    context = {'jur_name': jur_name,
               'patches': objects,
               'page_range': page_range,
               'alert_search': alert_search,
               'category_search': category_search,
               'applied_by_search': applied_by_search,
               'categories_': categories_,
               'alerts_': alerts_}
    return render(request, 'admintools/review_person_patches.html', context)


def list_all_person_patches(request, jur_name):
    patches = IssueResolverPatch.objects \
        .filter(jurisdiction__name__exact=jur_name)
    category_search = False
    alert_search = False
    applied_by_search = False
    status_search = False
    if request.GET.get('person'):
        person_ids = Person.objects.filter(
            memberships__organization__jurisdiction__name__exact=jur_name,
            name__icontains=request.GET.get('person'))
        patches = patches.filter(object_id__in=person_ids)
    if request.GET.get('category'):
        patches = patches.filter(category=request.GET.get('category'))
        category_search = request.GET.get('category')
    if request.GET.get('alert'):
        patches = patches.filter(alert=request.GET.get('alert'))
        alert_search = request.GET.get('alert')
    if request.GET.get('applied_by'):
        patches = patches.filter(applied_by=request.GET.get('applied_by'))
        applied_by_search = request.GET.get('applied_by')
    if request.GET.get('status'):
        patches = patches.filter(status=request.GET.get('status'))
        status_search = request.GET.get('status')
    objects, page_range = _get_pagination(patches.order_by('id'), request)
    categories_ = sorted(dict(IssueResolverPatch._meta.get_field(
        'category').choices).items())
    alerts_ = sorted(dict(IssueResolverPatch._meta.get_field(
        'alert').choices).items())
    status_ = sorted(dict(IssueResolverPatch._meta.get_field(
        'status').choices).items())
    context = {'jur_name': jur_name,
               'patches': objects,
               'page_range': page_range,
               'alert_search': alert_search,
               'category_search': category_search,
               'applied_by_search': applied_by_search,
               'status_search': status_search,
               'categories_': categories_,
               'status_': status_,
               'alerts_': alerts_}
    return render(request, 'admintools/list_person_patches.html', context)


def retire_legislators(request, jur_name):
    if request.method == 'POST':
        count = 0
        reconsider_person = []
        for k, v in request.POST.items():
            if v and not k.startswith('csrf'):
                p = Person.objects.get(id=k)
                # To make sure that provided retirement date is not less than
                # all of the existing end_dates
                prev = Membership.objects.filter(person=p,
                                                 end_date__gt=v).count()
                if prev:
                    reconsider_person.append(p)
                else:
                    mem = Membership.objects.filter(person=p, end_date='')
                    mem.update(end_date=v)
                    count += 1
        if count:
            messages.success(request, 'Successfully Retired {} '
                             'legislator(s)'.format(count))
        if reconsider_person:
            for person in reconsider_person:
                messages.error(request, 'Provide a valid Retirement Date for'
                               ' {}'.format(person.name))
    if request.GET.get('person'):
        people = Person.objects.filter(
            memberships__organization__jurisdiction__name__exact=jur_name,
            memberships__end_date='',
            name__icontains=request.GET.get('person')).distinct()
    else:
        people = Person.objects.filter(
            memberships__organization__jurisdiction__name__exact=jur_name,
            memberships__end_date='').distinct()
    objects, page_range = _get_pagination(people.order_by('name'), request)
    context = {'jur_name': jur_name,
               'people': objects,
               'page_range': page_range}
    return render(request, 'admintools/retire_legislators.html', context)


def list_retired_legislators(request, jur_name):
    if request.method == 'POST':
        count = 0
        reconsider_person = []
        for k, v in request.POST.items():
            if not k.startswith('csrf'):
                p = Person.objects.get(id=k)
                prev_retirement_date = Membership.objects.filter(
                    person=p).order_by('-end_date').first().end_date
                v = v.strip()
                if v:
                    # To make sure that provided retirement date is not less
                    # than the end_date, other than current retirement date
                    prev_date = Membership.objects \
                        .filter(person=p, end_date__lt=prev_retirement_date) \
                        .order_by('-end_date').first()
                    if prev_date:
                        if prev_date.end_date > v:
                            reconsider_person.append(p)
                            continue
                if prev_retirement_date != v:
                    Membership.objects.filter(
                        person=p, end_date=prev_retirement_date) \
                        .update(end_date=v)
                    count += 1
        if count:
            messages.success(request, 'Successfully Updated {} '
                             'Retired legislator(s)'.format(count))
        if reconsider_person:
            for person in reconsider_person:
                messages.error(request, 'Provide a valid Retirement Date for'
                               ' {}'.format(person.name))
    if request.GET.get('person'):
        people = Person.objects.filter(
            Q(memberships__organization__jurisdiction__name__exact=jur_name),
            ~Q(memberships__end_date=''),
            Q(name__icontains=request.GET.get('person'))).distinct()
    else:
        people = Person.objects.filter(
            Q(memberships__organization__jurisdiction__name__exact=jur_name) &
            ~Q(memberships__end_date='')).distinct()
    for person in people:
        if Membership.objects.filter(person=person, end_date=''):
            people = people.exclude(id=person.id)
    objects, page_range = _get_pagination(people.order_by('name'), request)
    people_with_end_date = {}
    for person in objects:
        people_with_end_date[person] = Membership.objects.filter(
            person=person).order_by('-end_date').first().end_date
    context = {'jur_name': jur_name,
               'people': people_with_end_date,
               'page_range': page_range}
    return render(request, 'admintools/list_retired_legislators.html', context)
