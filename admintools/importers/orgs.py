from opencivicdata.core.models import Organization, Membership
from admintools.models import DataQualityIssues


def create_org_issues(queryset, issue, alert):
    obj_list = []
    for query_obj in queryset:
        obj_list.append(
            DataQualityIssues(content_object=query_obj,
                              alert=alert,
                              issue=issue
                              )
        )
    DataQualityIssues.objects.bulk_create(obj_list)


def orgs_issues():
    issues = ['org_no_memberships', 'unmatched_org_person']
    for issue in issues:
        if issue == 'org_no_memberships':
            queryset = Organization.objects.filter(memberships__isnull=True)
            create_org_issues(queryset, issue, alert='error')
        else:
            queryset = Membership.objects.filter(person__isnull=True)
            create_org_issues(queryset, issue, alert='warning')
