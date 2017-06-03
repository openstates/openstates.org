from opencivicdata.legislative.models import Bill
from admintools.models import DataQualityIssues
from django.contrib.contenttypes.models import ContentType


def create_bill_issues(queryset, issue, alert):
    obj_list = []
    for query_obj in queryset:
        contenttype_obj = ContentType.objects.get_for_model(query_obj)
        if not DataQualityIssues.objects.filter(object_id=query_obj.id,
                                                content_type=contenttype_obj,
                                                alert=alert, issue=issue):
            obj_list.append(
                DataQualityIssues(content_object=query_obj,
                                  alert=alert,
                                  issue=issue
                                  )
            )
    print("Found New Issues: {}".format(len(obj_list)))
    DataQualityIssues.objects.bulk_create(obj_list)


def bills_issues():
    issues = ['no_actions',
              'no_sponsors',
              'unmatched_person_sponsor',
              'unmatched_org_sponsor',
              'no_versions']

    for issue in issues:
        if issue == 'no_actions':
            print("importing bills with no actions...")

            queryset = Bill.objects.filter(actions__isnull=True)
            create_bill_issues(queryset, issue, alert='error')

        elif issue == 'no_sponsors':
            print("importing bills with no sponsors...")

            queryset = Bill.objects.filter(sponsorships__isnull=True)
            create_bill_issues(queryset, issue, alert='warning')

        elif issue == 'unmatched_person_sponsor':
            print("importing bills with unmatched person sponsors...")

            queryset = Bill.objects.filter(sponsorships__person__isnull=True,
                                           sponsorships__entity_type='person').distinct()
            create_bill_issues(queryset, issue, alert='warning')

        elif issue == 'unmatched_org_sponsor':
            print("importing bills with unmatched org sponsors...")

            queryset = Bill.objects.filter(sponsorships__organization__isnull=True,
                                           sponsorships__entity_type='organization').distinct()
            create_bill_issues(queryset, issue, alert='warning')
        else:
            print("importing bills with no version..")

            queryset = Bill.objects.filter(versions__isnull=True)
            create_bill_issues(queryset, issue, alert='error')
