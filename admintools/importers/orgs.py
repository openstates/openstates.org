from admintools.issues import IssueType
from opencivicdata.core.models import Organization, Membership
from admintools.models import DataQualityIssue
from django.contrib.contenttypes.models import ContentType


def create_org_issues(queryset, issue):
    obj_list = []
    alert = IssueType.level_for(issue)
    issue = IssueType.class_for(issue) + '-' + issue
    for query_obj in queryset:
        contenttype_obj = ContentType.objects.get_for_model(query_obj)
        if not DataQualityIssue.objects.filter(object_id=query_obj.id,
                                               content_type=contenttype_obj,
                                               alert=alert, issue=issue):
            obj_list.append(
                DataQualityIssue(content_object=query_obj, alert=alert,
                                 issue=issue)
            )
    print("Found New Issues: {}".format(len(obj_list)))
    DataQualityIssue.objects.bulk_create(obj_list)


def orgs_issues():
    for issue in IssueType.get_issues_for('organization'):
        if issue == 'no-memberships':
            print("importing orgs with no memberships...")
            queryset = Organization.objects.filter(memberships__isnull=True)
            create_org_issues(queryset, issue)

        else:
            print("importing orgs with unmatched person...")
            queryset = Membership.objects.filter(person__isnull=True)
            create_org_issues(queryset, issue)
