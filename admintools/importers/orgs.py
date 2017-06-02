from opencivicdata.core.models import Organization, Membership
from admintools.models import DataQualityIssues
from django.contrib.contenttypes.models import ContentType


def create_org_issues(queryset, issue, alert):
    for query_obj in queryset:
        contenttype_obj = ContentType.objects.get_for_model(query_obj)
        if not DataQualityIssues.objects.filter(object_id=query_obj.id, content_type=contenttype_obj):
            DataQualityIssues.objects.create(content_object=query_obj,
                                             alert=alert,
                                             issue=issue
                                             )


def orgs_issues():
    issues = ['org_no_memberships', 'unmatched_org_person']
    for issue in issues:
        if issue == 'org_no_memberships':
            queryset = Organization.objects.filter(memberships__isnull=True)
            create_org_issues(queryset, issue, alert='error')
        else:
            queryset = Membership.objects.filter(person__isnull=True)
            create_org_issues(queryset, issue, alert='warning')
