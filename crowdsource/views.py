from django.shortcuts import render

from django.db.models import Count
from opencivicdata.legislative.models import Bill, VoteEvent

from .issues import IssueType
from .models import CrowdSourceIssue, CrowdSourceIssueResolver
from .forms import IssueForm, ResolverForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


def reporter_utility(issue_type, identifier):
    content_object = None
    if issue_type == 'bill':
        content_object = Bill.objects.get(id=identifier)
    elif issue_type == 'voteevent':
        content_object = VoteEvent.objects.get(id=identifier)
    return content_object

def already_exists(object_id,issue):
        try:
            CrowdSourceIssue.objects.get(object_id=object_id, issue=issue,
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
            issue.content_object = reporter_utility(issue_type, issue.object_id)
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
            exist_resolver = CrowdSourceIssueResolver.objects.filter(issue = resolver.issue,
                                                new_value=resolver.new_value)
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
