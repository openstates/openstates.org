from opencivicdata.core.models import Organization, Membership
from admintools.models import DataQualityIssues


def create_org_issues(queryset, issue, alert):
    obj_list = []
    for query_obj in queryset:
        if not DataQualityIssues.objects.filter(related_ids__contains=[query_obj.id],
                                                alert=alert, issue=issue):
            obj_list.append(
                DataQualityIssues(related_ids=[query_obj.id],
                                  alert=alert,
                                  issue=issue
                                  )
            )
    print("Found New Issues: {}".format(len(obj_list)))
    DataQualityIssues.objects.bulk_create(obj_list)


def orgs_issues():
    issues = ['org_no_memberships', 'unmatched_org_person']
    for issue in issues:
        if issue == 'org_no_memberships':
            print("importing orgs with no memberships...")

            queryset = Organization.objects.filter(memberships__isnull=True)
            create_org_issues(queryset, issue, alert='error')
        else:
            print("importing orgs with unmatched person...")

            queryset = Membership.objects.filter(person__isnull=True)
            create_org_issues(queryset, issue, alert='warning')
