from django.shortcuts import render

from django.db.models import Q
from opencivicdata.legislative.models import Bill, VoteEvent
from opencivicdata.core.models import Jurisdiction, Person

from .issues import IssueType
from dataquality.models import DataQualityIssue, IssueResolverPatch
from .forms import IssueForm, ResolverForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


def get_object_by_identifier(issue_type, identifier):
    content_object = None
    if issue_type == 'bill':
        content_object = Bill.objects.filter(id=identifier)
    elif issue_type == 'voteevent':
        content_object = VoteEvent.objects.filter(id=identifier)
    elif issue_type == 'person':
        content_object = Person.objects.filter(id=identifier)
    return content_object

def already_exists(object_id,issue):
        try:
            DataQualityIssue.objects.get(object_id=object_id, issue=issue,
                                         status='active')
            return True
        except:
            return False

@csrf_exempt
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
                messages.error(request, "Object with '%s' object id not found."%issue.object_id) 
                return render(request, 'report.html', {'form': post_form, 'headline': "NewIssue"})
            issue.save()
            messages.success(request, "Issue Successfully Created")
            return render(request, 'report.html', {'form': form, 'headline': "New Issue"})
        else:
            errors = post_form.errors.as_data()
            for error in errors:
                messages.error(request, error+": "+errors[error])
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
            # user with one email can only create one resolver for a particular issue, otherwise he can edit it
            exist_resolver = CrowdSourceIssueResolver.objects.filter(Q(issue = resolver.issue,
                                                new_value=resolver.new_value) | Q(issue = resolver.issue,
                                                reporter_email=resolver.reporter_email))
            if exist_resolver.count() > 0:
                messages.error(request, "Resolver with the updates already exists.")
                return render(request, 'report.html', {'form': post_form, 'headline': "New Resolver"})
            resolver.save()
            messages.success(request, "Resolve Submitted Successfully !")
            return render(request, 'report.html', {'form': form, 'headline': "New Resolver"})
        else:
            errors = post_form.errors.as_data()
            for error in errors:
                messages.error(request, error+": "+errors[error])
            return render(request, 'report.html', {'form': post_form, 'headline': "New Resolver"})
        
    else:
        return render(request, 'report.html', {'form': form, 'headline': "New Resolver"})


