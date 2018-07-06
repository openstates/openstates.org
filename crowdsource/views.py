from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages

from opencivicdata.legislative.models import Bill, VoteEvent
from opencivicdata.core.models import Person
from dataquality.models import DataQualityIssue, IssueResolverPatch

from .issues import IssueType
from .forms import IssueForm, ResolverForm


def get_object_by_identifier(issue_type, identifier):
    content_object = None
    if issue_type == 'community-person':
        content_object = Person.objects.filter(id=identifier)
    if issue_type == 'community-bill':
        content_object = Bill.objects.filter(id=identifier)
    elif issue_type == 'commmunity-voteevent':
        content_object = VoteEvent.objects.filter(id=identifier)
    return content_object


def already_exists(object_id, issue):
        exists = True
        try:
            DataQualityIssue.objects.get(object_id=object_id, issue=issue,
                                         status='active')
        except DataQualityIssue.DoesNotExist:
            exists = False
        return exists


def check_old_value_person(person, category, old_value):
    if category == 'name':
        return (old_value == person.name)
    elif category == 'image':
        return (old_value == person.image)
    else:
        contacts = person.contact_details.filter(type=category)
        for contact in contacts:
            if contact.value == old_value:
                return True
    return False


def report_issue(request):

    form = IssueForm()
    if request.method == 'POST':
        post = request.POST
        post_form = IssueForm(post)
        active_issue_exists = already_exists(post['object_id'], post['issue'])
        if post_form.is_valid() and not active_issue_exists:
            issue = post_form.save(commit=False)
            issue_type = IssueType.class_for(issue.issue)
            content_object = get_object_by_identifier(issue_type, issue.object_id)
            if content_object:
                issue.content_object = content_object[0]
            else:
                messages.error(request, "Object with '%s' object id not found." % issue.object_id)
                return render(request, 'report.html', {'form': post_form, 'headline': "NewIssue"})
            issue.save()
            messages.success(request, "Issue Successfully Created")
            return render(request, 'report.html', {'form': form, 'headline': "New Issue"})
        else:
            errors = post_form.errors.as_data()
            for error in errors:
                messages.error(request, error+": "+str(errors[error]))
            if active_issue_exists:
                messages.error(request, "Issue for the object already exists.")
            return render(request, 'report.html', {'form': post_form, 'headline': "New Issue"})
    else:
        return render(request, 'report.html', {'form': form, 'headline': "New Issue"})


def submit_resolve(request):

    form = ResolverForm()
    if request.method == 'POST':
        post = request.POST
        post_form = ResolverForm(post)
        if post_form.is_valid():
            resolver = post_form.save(commit=False)

            try:
                content_object = Person.objects.get(id=resolver.object_id)
                resolver.content_object = content_object
            except Person.DoesNotExist:
                messages.error(request, "Object with '%s' object id not found."
                               % resolver.object_id)
                return render(request, 'report.html', {'form': post_form,
                                                       'headline': "New Resolver"})

            if not check_old_value_person(resolver.content_object, resolver.category,
                                          resolver.old_value):
                messages.error(request, "Old value doesn't match with value in database")
                return render(request, 'report.html', {'form': post_form,
                                                       'headline': "New Resolver"})

            # user with one email can only create only one resolver for an object
            # with unreviewed status same set of old_value and new_value can't
            # be created with unreviewed status(default after creation)
            exist_resolver = IssueResolverPatch.objects.filter(
                                    Q(old_value=resolver.old_value,
                                      status="unreviewed",
                                      new_value=resolver.new_value,
                                      category=resolver.category,
                                      object_id=resolver.object_id) |
                                    Q(object_id=resolver.object_id,
                                      status="unreviewed",
                                      reporter_email=resolver.reporter_email,
                                      category=resolver.category))
            if exist_resolver.count() > 0:
                messages.error(request, "Either Same new value has already been requested or"
                                        " you already have resolver with the given object_id")
                return render(request, 'report.html', {'form': post_form,
                                                       'headline': "New Resolver"})

            resolver.status = "unreviewed"
            resolver.save()
            messages.success(request, "Resolve Submitted Successfully !")
            return render(request, 'report.html', {'form': form, 'headline': "New Resolver"})
        else:
            errors = post_form.errors.as_data()
            for error in errors:
                messages.error(request, error+": "+str(errors[error]))
            return render(request, 'report.html', {'form': post_form, 'headline': "New Resolver"})

    else:
        object_id = request.GET.get('object_id')
        jurisdiction = request.GET.get('jurisdiction')
        form.initial = {
            'object_id': object_id,
            'jurisdiction': jurisdiction
        }
        return render(request, 'report.html', {'form': form, 'headline': "New Resolver"})


def list_issues(request):
    issues = DataQualityIssue.objects.filter(
             issue__in=IssueType.get_issues_for("community-person"))
    return render(request, 'list_issues.html', {'issues': issues})
