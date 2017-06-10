from admintools.issues import IssueType
from opencivicdata.core.models import Jurisdiction, Organization, Membership
from admintools.models import DataQualityIssue


def create_org_issues(queryset, issue, jur):
    obj_list = []
    alert = IssueType.level_for(issue)
    issue = IssueType.class_for(issue) + '_' + issue
    for query_obj in queryset:
        if not DataQualityIssue.objects.filter(object_id=query_obj.id,
                                               alert=alert, issue=issue,
                                               jurisdiction=jur):
            obj_list.append(
                DataQualityIssue(content_object=query_obj, alert=alert,
                                 issue=issue, jurisdiction=jur)
            )
    DataQualityIssue.objects.bulk_create(obj_list)
    return len(obj_list)


def orgs_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        count = 0
        for issue in IssueType.get_issues_for('organization'):
            if issue == 'no_memberships':
                queryset = Organization.objects.filter(jurisdiction=jur,
                                                       memberships__isnull=True)
                count += create_org_issues(queryset, issue, jur)

            else:
                queryset = Membership.objects.filter(organization__jurisdiction=jur,
                                                     person__isnull=True)
                count += create_org_issues(queryset, issue, jur)
        print("Imported Organization Related {} Issues for {}".format(count, jur.name))
