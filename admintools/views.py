from django.shortcuts import render
from pupa.models import RunPlan
from opencivicdata.core.models import (Jurisdiction, Person, Organization,
                                       Membership, PersonName, Post)
from opencivicdata.legislative.models import (Bill, VoteEvent, BillSponsorship,
                                              LegislativeSession, PersonVote)
from admintools.issues import IssueType
from admintools.models import DataQualityIssue, IssueResolverPatch
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from collections import defaultdict, Counter
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db import transaction
import datetime

# Basic Classes with their Identifiers.
upstream = {'person': Person,
            'organization': Organization,
            'membership': Membership,
            'bill': Bill,
            'voteevent': VoteEvent,
            'post': Post}


# get run status for a jurisdiction
def _get_run_status(jur):
    runs = RunPlan.objects.filter(jurisdiction=jur).order_by('-end_time')
    latest_date = runs.first().end_time.date()
    status = 0
    for run in runs:
        if run.success:
            break
        else:
            status += 1
    return {'count': None if status == 1 else status, 'date': latest_date}


# validate date in YYYY-MM-DD format.
def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


# get pagination of results upto 20 objects
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
    all_counts = DataQualityIssue.objects.filter(status='active').values(
        'jurisdiction', 'issue', 'alert').annotate(Count('issue'))
    for counts in all_counts:
        jur = Jurisdiction.objects.get(id=counts['jurisdiction'])
        rows.setdefault(counts['jurisdiction'], {})['jur_name'] = jur.name
        rows[counts['jurisdiction']].setdefault(
            counts['issue'].split('-')[0], {})
        rows[counts['jurisdiction']][counts['issue'].split('-')[0]][
            counts['alert']] = rows[counts['jurisdiction']][
                counts['issue'].split('-')[0]].get(
                    counts['alert'], 0) + counts['issue__count']

        if not rows[counts['jurisdiction']].get('run'):
            rows[counts['jurisdiction']]['run'] = _get_run_status(jur)

    # RunPlan For those who don't have any type of dataquality_issues
    rest_jurs = Jurisdiction.objects.exclude(id__in=rows.keys())
    for jur in rest_jurs:
        rows[jur.id] = {}
        rows[jur.id]['jur_name'] = jur.name
        rows[jur.id]['run'] = _get_run_status(jur)
    rows = sorted(rows.items(),  key=lambda v: v[1]['jur_name'])
    return render(request, 'admintools/index.html', {'rows': rows})


# Calculates all active dataquality_issues in given jurisdiction
def _jur_dataquality_issues(jur_id):
    cards = defaultdict(dict)
    exceptions = defaultdict(dict)
    issues = IssueType.choices()
    for issue, description in issues:
        related_class = IssueType.class_for(issue)
        cards[related_class][issue] = {}
        exceptions[related_class][issue] = {}
        issue_type = IssueType.class_for(issue) + '-' + issue
        alert = IssueType.level_for(issue)
        cards[related_class][issue]['alert'] = True if alert == 'error' \
            else False
        exceptions[related_class][issue]['alert'] = True if alert == 'error' \
            else False
        cards[related_class][issue]['description'] = description
        exceptions[related_class][issue]['description'] = description
        ct_obj = ContentType.objects.get_for_model(upstream[related_class])
        j = Jurisdiction.objects.filter(
            id=jur_id, dataquality_issues__status='active',
            dataquality_issues__content_type=ct_obj,
            dataquality_issues__issue=issue_type).annotate(_issues=Count(
                'dataquality_issues'))
        cards[related_class][issue]['count'] = j[0]._issues if j else 0
        je = Jurisdiction.objects.filter(
            id=jur_id, dataquality_issues__status='ignored',
            dataquality_issues__content_type=ct_obj,
            dataquality_issues__issue=issue_type).annotate(_issues=Count(
                'dataquality_issues'))
        exceptions[related_class][issue]['count'] = je[0]._issues if je else 0
    return dict(cards), dict(exceptions)


# Jurisdiction Specific Page
def jurisdiction_intro(request, jur_id):
    issues, exceptions = _jur_dataquality_issues(jur_id)
    bill_from_orgs_list = Bill.objects.filter(
        legislative_session__jurisdiction__id=jur_id) \
        .values('from_organization__name').distinct()

    voteevent_orgs_list = VoteEvent.objects.filter(
        legislative_session__jurisdiction__id=jur_id) \
        .values('organization__name').distinct()

    orgs_list = Organization.objects.filter(
        jurisdiction__id=jur_id).values('classification').distinct()

    context = {'jur_id': jur_id,
               'cards': issues,
               'exceptions': exceptions,
               'bill_orgs': bill_from_orgs_list,
               'voteevent_orgs': voteevent_orgs_list,
               'orgs': orgs_list,
               }
    return render(request, 'admintools/jurisdiction_intro.html', context)


# Bills and VoteEvents related info for a session
def legislative_session_info(request, jur_id, identifier):
    session = LegislativeSession.objects.get(
        jurisdiction__id=jur_id, identifier=identifier)

    bill_from_orgs_list = Bill.objects.filter(
        legislative_session__jurisdiction__id=jur_id,
        legislative_session__identifier=identifier) \
        .values('from_organization__name').distinct()

    voteevent_orgs_list = VoteEvent.objects.filter(
        legislative_session__jurisdiction__id=jur_id,
        legislative_session__identifier=identifier) \
        .values('organization__name').distinct()

    context = {
        'jur_id': jur_id,
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
    if request.GET.get('post_role'):
        query &= Q(role__icontains=request.GET.get('post_role'))
    if request.GET.get('post_label'):
        query &= Q(label__icontains=request.GET.get('post_label'))
    return query


# Lists given issue(s) related objetcs
def list_issue_objects(request, jur_id, related_class, issue_slug):
    description = IssueType.description_for(issue_slug)
    issue = IssueType.class_for(issue_slug) + '-' + issue_slug
    objects_list = DataQualityIssue.objects.filter(
        jurisdiction_id=jur_id,
        status='active',
        issue=issue).values_list('object_id', flat=True)
    cards = upstream[related_class].objects.filter(id__in=objects_list)
    if request.GET:
        cards = cards.filter(_filter_results(request))
    objects, page_range = _get_pagination(cards.order_by('id'), request)

    # url_slug used to address the Django-admin page
    if related_class in ['person', 'organization', 'post']:
        url_slug = 'core_' + related_class + '_change'
    elif related_class in ['bill', 'voteevent']:
        url_slug = 'legislative_' + related_class + '_change'
    else:
        # because we don't have membership objetcs listed on Django-admin panel
        # so redirect to related organization page
        url_slug = None

    context = {'jur_id': jur_id,
               'issue_slug': issue_slug,
               'objects': objects,
               'description': description,
               'page_range': page_range,
               'url_slug': url_slug,
               'related_class': related_class}
    return render(request, 'admintools/list_issues.html', context)


# prepare data to be loaded into main DB.
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


# creates `unreviewed` patches into DB applied_by `admin` for `missing` values.
@transaction.atomic
def person_resolve_issues(request, jur_id, issue_slug):
    if request.method == 'POST':
        if issue_slug == 'missing-phone':
            category = 'voice'
        elif issue_slug == 'missing-photo':
            category = 'image'
        elif issue_slug in ['missing-email', 'missing-address']:
            category = issue_slug[8:]
        else:
            raise ValueError("Person Resolver needs update for new issue.")
        jur = Jurisdiction.objects.get(id=jur_id)
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
        if issue_items:
            messages.success(request, 'Successfully created {} {}(s) Admin '
                             'Patch(es)'.format(len(issue_items),
                                                IssueType.description_for(
                                                  issue_slug)))
    return HttpResponseRedirect(reverse('list_issue_objects',
                                        args=(jur_id, 'person',
                                              issue_slug)))


# lists `unreviewed` patches for review.
def review_person_patches(request, jur_id):
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
        .filter(status='unreviewed', jurisdiction_id=jur_id)

    # To maintain applied filter in template
    category_search = False
    alert_search = False
    applied_by_search = False
    # Filters Results
    if request.GET.get('person'):
        person_ids = Person.objects.filter(
            memberships__organization__jurisdiction_id=jur_id,
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

    context = {'jur_id': jur_id,
               'patches': objects,
               'page_range': page_range,
               'alert_search': alert_search,
               'category_search': category_search,
               'applied_by_search': applied_by_search,
               'categories_': categories_,
               'alerts_': alerts_}
    return render(request, 'admintools/review_person_patches.html', context)


# list all patches and functionality to modify `status`.
def list_all_person_patches(request, jur_id):
    if request.method == 'POST':
        count = 0
        for k, v in request.POST.items():
            if not k.startswith('csrf'):
                pa = IssueResolverPatch.objects.get(id=k)
                # if category is `name` or `image` and updated status is
                # approved then make sure to display error if there is already
                # a approved patch is present.
                if pa.category in ['image', 'name'] and v == 'approved' \
                        and pa.status != v:
                    hg = IssueResolverPatch.objects \
                        .filter(jurisdiction_id=jur_id, object_id=pa.object_id,
                                category=pa.category, status='approved')
                    if hg:
                        per = Person.objects.get(id=pa.object_id)
                        messages.error(request, "Multiple Approved Pathces for"
                                       " {} ({})".format(per.name, pa.category)
                                       )
                        continue
                # if `status` is changed.
                if pa.status != v:
                    pa.status = v
                    pa.save()
                    count += 1
        if count:
            messages.success(request, "Successfully Updated Status of "
                             "{} Patch(es)".format(count))

    patches = IssueResolverPatch.objects \
        .filter(jurisdiction_id=jur_id)
    # To maintain applied filter in template
    category_search = False
    alert_search = False
    applied_by_search = False
    status_search = False
    # Filter Results
    if request.GET.get('person'):
        person_ids = Person.objects.filter(
            memberships__organization__jurisdiction_id=jur_id,
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

    context = {'jur_id': jur_id,
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


# To retire legislator(s)
def retire_legislators(request, jur_id):
    if request.method == 'POST':
        count = 0
        for k, v in request.POST.items():
            if v and not k.startswith('csrf'):
                v = v.replace('/', '-')
                # validate date in YYYY-MM-DD format
                resp = validate_date(v)
                p = Person.objects.get(id=k)
                if resp:
                    # To make sure that provided retirement date is not less
                    # than all of the existing end_dates
                    prev = p.memberships.filter(end_date__gt=v).count()
                    if prev:
                        messages.error(request, 'Provide a valid Retirement '
                                       'Date for {}'.format(p.name))
                    else:
                        mem = p.memberships.filter(end_date='')
                        mem.update(end_date=v)
                        count += 1
                else:
                    messages.error(request, 'Provide a valid Retirement '
                                   'Date for {}'.format(p.name))
        if count:
            messages.success(request, 'Successfully Retired {} '
                             'legislator(s)'.format(count))
    if request.GET.get('person'):
        people = Person.objects.filter(
            memberships__organization__jurisdiction_id=jur_id) \
                .filter(memberships__end_date='',
                        name__icontains=request.GET.get('person')).distinct()
    else:
        people = Person.objects.filter(
            memberships__organization__jurisdiction_id=jur_id) \
            .filter(memberships__end_date='').distinct()

    objects, page_range = _get_pagination(people.order_by('name'), request)
    context = {'jur_id': jur_id,
               'people': objects,
               'page_range': page_range}
    return render(request, 'admintools/retire_legislators.html', context)


# List all the retire legislator(s) and functionality to update/unretire them.
def list_retired_legislators(request, jur_id):
    if request.method == 'POST':
        count = 0
        for k, v in request.POST.items():
            if not k.startswith('csrf'):
                p = Person.objects.get(id=k)
                prev_retirement_date = p.memberships.order_by(
                    '-end_date').first().end_date
                v = v.replace('/', '-')
                # validate date in YYYY-MM-DD format
                resp = validate_date(v)
                if resp or v == '':
                    if v:
                        if resp:
                            # To make sure that provided retirement date is not
                            # less than the end_date, other than current
                            # retirement date
                            prev_date = p.memberships.filter(
                                end_date__lt=prev_retirement_date).order_by(
                                    '-end_date').first()
                            if prev_date:
                                if prev_date.end_date > v:
                                    messages.error(request, 'Provide a valid '
                                                   'Retirement Date for '
                                                   '{}'.format(p.name))
                                    continue
                        else:
                            messages.error(request,
                                           'Provide a valid Retirement Date'
                                           ' for {}'.format(p.name))
                    if prev_retirement_date != v:
                        p.memberships.filter(end_date=prev_retirement_date) \
                            .update(end_date=v)
                        count += 1
                else:
                    messages.error(request,
                                   'Provide a valid Retirement Date'
                                   ' for {}'.format(p.name))
        if count:
            messages.success(request, 'Successfully Updated {} '
                             'Retired legislator(s)'.format(count))

    if request.GET.get('person'):
        people = Person.objects.filter(
            memberships__organization__jurisdiction_id=jur_id) \
            .filter(~Q(memberships__end_date=''),
                    Q(name__icontains=request.GET.get('person'))).distinct()
    else:
        people = Person.objects.filter(
            memberships__organization__jurisdiction_id=jur_id) \
            .filter(~Q(memberships__end_date='')).distinct()

    people_with_end_date = {}
    for person in people:
        people_with_end_date[person] = person.memberships.order_by(
            '-end_date').first().end_date
    objects, page_range = _get_pagination(tuple(people_with_end_date.items()),
                                          request)
    context = {'jur_id': jur_id,
               'people': objects,
               'page_range': page_range}
    return render(request, 'admintools/list_retired_legislators.html', context)


# Name Resolution Tool
def name_resolution_tool(request, jur_id, category):
    if request.method == 'POST':
        count = 0
        for name, pid in request.POST.items():
            if pid and not name.startswith('csrf'):
                PersonName.objects.create(person_id=pid, name=name,
                                          note='added via name resolution tool'
                                          )
                person = Person.objects.get(pk=pid)
                if 'other_names' not in person.locked_fields:
                    person.locked_fields.append('other_names')
                    person.save()
                if category == 'unmatched_bill_sponsors':
                    sp = BillSponsorship.objects.filter(entity_type='person',
                                                        person_id=None,
                                                        name=name)
                    sp.update(person_id=pid)
                elif category == 'unmatched_voteevent_voters':
                    vs = PersonVote.objects.filter(voter_id=None,
                                                   voter_name=name)
                    vs.update(voter_id=pid)
                elif category == 'unmatched_memberships':
                    mem = Membership.objects.filter(person_id=None,
                                                    person_name=name)
                    mem.update(person_id=pid)
                else:
                    raise ValueError('Name Resolution Tool needs update'
                                     ' for new category')
                count += 1
        messages.success(request, 'Successfully Updated {} '
                         'Umatched legislator(s)'.format(count))

    unresolved = Counter()
    session_search = False
    session_id = request.GET.get('session_id')

    if category != 'unmatched_memberships' and \
            not session_id and not session_id == 'all':
        # By Default:- Filter By Latest Legislative Session
        session_id = LegislativeSession.objects.filter(
            jurisdiction_id=jur_id).order_by('-identifier') \
            .first().identifier
    if category == 'unmatched_bill_sponsors':
        queryset = BillSponsorship.objects \
            .filter(
                bill__legislative_session__jurisdiction_id=jur_id,
                entity_type='person',
                person_id=None).annotate(num=Count('name'))
        if session_id != 'all':
            queryset = queryset.filter(
                bill__legislative_session__identifier=session_id)
        session_search = session_id
        # Calculates how many times a unmatched name appeared.
        for obj in queryset:
            unresolved[obj.name] += obj.num

    elif category == 'unmatched_voteevent_voters':
        queryset = PersonVote.objects \
            .filter(
                vote_event__legislative_session__jurisdiction_id=jur_id,
                voter_id=None).annotate(num=Count('voter_name'))
        if session_id != 'all':
            queryset = queryset.filter(
                vote_event__legislative_session__identifier=session_id)
        session_search = session_id
        # Calculates how many times a unmatched name appeared.
        for obj in queryset:
            unresolved[obj.voter_name] += obj.num

    elif category == 'unmatched_memberships':
        queryset = Membership.objects.filter(
            organization__jurisdiction_id=jur_id,
            person_id=None
        ).annotate(num=Count('person_name'))

        # Calculates how many times a unmatched name appeared.
        for obj in queryset:
            unresolved[obj.person_name] += obj.num
    else:
        raise ValueError('Name Resolution Tool needs update'
                         ' for new category')

    # convert unresolved to a normal dict so it's iterable in template
    unresolved = sorted(((k, v) for (k, v) in unresolved.items()),
                        key=lambda x: x[1], reverse=True)

    objects, page_range = _get_pagination(unresolved, request)
    people = Person.objects.filter(
        memberships__organization__jurisdiction_id=jur_id) \
        .order_by('name').distinct()
    context = {
        'jur_id': jur_id,
        'people': people,
        'unresolved': objects,
        'page_range': page_range,
        'category': category,
        'session_search': session_search,
    }
    return render(request, 'admintools/unresolved.html', context)


# create a `unreviewed` patch for wrong values.
def create_person_patch(request, jur_id):
    if request.method == 'POST':
        p = Person.objects.get(id=request.POST['person'])
        # if any error occur then `create` will throw error.
        IssueResolverPatch.objects.create(
            content_object=p,
            jurisdiction_id=jur_id,
            status='unreviewed',
            old_value=request.POST['old_value'],
            new_value=request.POST['new_value'],
            source=request.POST.get('source'),
            category=request.POST['category'],
            alert='error',
            note=request.POST.get('note'),
            applied_by='admin',
        )
        messages.success(request, "Successfully created Patch")
    people = Person.objects.filter(
        memberships__organization__jurisdiction_id=jur_id).distinct()
    context = {'jur_id': jur_id,
               'people': people}
    return render(request, 'admintools/create_person_patch.html', context)


# Data Quality Exceptions
def dataquality_exceptions(request, jur_id, issue_slug, action):
    related_class = IssueType.class_for(issue_slug)
    issue = related_class + '-' + issue_slug
    if request.method == 'POST':
        if action == 'add':
            msg = request.POST['message']
            ids = [key for key in request.POST if not key.startswith('csrf')
                   and not key == 'message']
            DataQualityIssue.objects.filter(jurisdiction_id=jur_id,
                                            object_id__in=ids, issue=issue,
                                            status='active').update(
                                                status='ignored', message=msg)
            messages.success(request, "Successfully Ignored {} Issue(s)"
                             .format(len(request.POST) - 2))
            return HttpResponseRedirect(reverse('list_issue_objects',
                                                args=(jur_id, related_class,
                                                      issue_slug)))
        elif action == 'remove':
            ids = []
            # keys = msg__@#$__ocd-id1__@#$__ocd-id2
            for keys in request.POST.keys():
                if not keys.startswith('csrf'):
                    ids = keys.split('__@#$__')
                    msg = ids[0]
                    ids.remove(ids[0])
                    DataQualityIssue.objects.filter(jurisdiction_id=jur_id,
                                                    object_id__in=ids,
                                                    issue=issue,
                                                    status='ignored',
                                                    message=msg).update(
                                                        status='active',
                                                        message='')
            if ids:
                messages.success(request, "Successfully Activated {} "
                                 "Issue(s)".format(len(ids)))
            return HttpResponseRedirect(reverse('dataquality_exceptions',
                                                args=(jur_id, issue_slug,
                                                      'remove')))

    else:
        description = IssueType.description_for(issue_slug)
        objects_list = DataQualityIssue.objects.filter(
                        jurisdiction_id=jur_id,
                        status='ignored',
                        issue=issue).values_list('object_id', flat=True)
        if request.GET:
            if request.GET.get('message'):
                objects_list = objects_list.filter(
                    message__icontains=request.GET['message'])
            cards = upstream[related_class].objects.filter(
                id__in=objects_list)
            cards = cards.filter(_filter_results(request))
        else:
            cards = upstream[related_class].objects.filter(id__in=objects_list)
        data = defaultdict(list)
        for card in cards:
            msg = DataQualityIssue.objects.get(object_id=card.id,
                                               issue=issue).message
            data[msg].append(card)
        objects, page_range = _get_pagination(tuple(data.items()), request)
        # url_slug used to address the Django-admin page
        if related_class in ['person', 'organization', 'post']:
            url_slug = 'core_' + related_class + '_change'
        elif related_class in ['bill', 'voteevent']:
            url_slug = 'legislative_' + related_class + '_change'
        else:
            # because we don't have membership objetcs listed on Django-admin
            # panel. so redirect to related organization page
            url_slug = None
        context = {'jur_id': jur_id,
                   'issue_slug': issue_slug,
                   'objects': objects,
                   'description': description,
                   'page_range': page_range,
                   'url_slug': url_slug,
                   'related_class': related_class}
        return render(request, 'admintools/list_dataquality_exceptions.html',
                      context)
