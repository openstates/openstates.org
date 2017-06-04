from admintools.issues import IssueType
from opencivicdata.legislative.models import Bill
from admintools.models import DataQualityIssue
from django.contrib.contenttypes.models import ContentType


def create_bill_issues(queryset, issue):
    obj_list = []
    alert = IssueType.level_for(issue)
    issue = IssueType.class_for(issue) + ' - ' + issue
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


def bills_issues():
    for issue in IssueType.get_issues_for('bill'):
        if issue == 'no-actions':
            print("importing bills with no actions...")

            queryset = Bill.objects.filter(actions__isnull=True)
            create_bill_issues(queryset, issue)

        elif issue == 'no-sponsors':
            print("importing bills with no sponsors...")

            queryset = Bill.objects.filter(sponsorships__isnull=True)
            create_bill_issues(queryset, issue)

        elif issue == 'unmatched-person-sponsor':
            print("importing bills with unmatched person sponsors...")

            queryset = Bill.objects.filter(sponsorships__entity_type='person',
                                           sponsorships__person__isnull=True).distinct()
            create_bill_issues(queryset, issue)

        elif issue == 'unmatched-org-sponsor':
            print("importing bills with unmatched org sponsors...")

            queryset = Bill.objects.filter(sponsorships__entity_type='organization',
                                           sponsorships__organization__isnull=True).distinct()
            create_bill_issues(queryset, issue)
        else:
            print("importing bills with no version..")

            queryset = Bill.objects.filter(versions__isnull=True)
            create_bill_issues(queryset, issue)
