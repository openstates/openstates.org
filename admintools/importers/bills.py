from admintools.issues import IssueType
from opencivicdata.legislative.models import Bill
from admintools.models import DataQualityIssue
from opencivicdata.core.models import Jurisdiction


def create_bill_issues(queryset, issue, jur):
    obj_list = []
    alert = IssueType.level_for(issue)
    issue = IssueType.class_for(issue) + '-' + issue
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


def bills_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                        issue__startswith='bill-').delete()
        bills = Bill.objects.filter(legislative_session__jurisdiction=jur)
        count = 0
        for issue in IssueType.get_issues_for('bill'):
            if issue == 'no-actions':
                queryset = bills.filter(actions__isnull=True)
                count += create_bill_issues(queryset, issue, jur)
            elif issue == 'no-sponsors':
                queryset = bills.filter(sponsorships__isnull=True)
                count += create_bill_issues(queryset, issue, jur)
            elif issue == 'unmatched-person-sponsor':
                queryset = bills.filter(sponsorships__entity_type='person',
                                        sponsorships__person__isnull=True) \
                                        .distinct()
                count += create_bill_issues(queryset, issue, jur)
            elif issue == 'unmatched-org-sponsor':
                queryset = bills \
                    .filter(sponsorships__entity_type='organization',
                            sponsorships__organization__isnull=True).distinct()
                count += create_bill_issues(queryset, issue, jur)
            elif issue == 'no-versions':
                queryset = bills.filter(versions__isnull=True)
                count += create_bill_issues(queryset, issue, jur)
            else:
                raise ValueError("Bill Importer needs update for new issue.")
        print("Imported Bills Related {} Issues for {}".format(count,
                                                               jur.name))
