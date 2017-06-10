from opencivicdata.core.models import Jurisdiction
from admintools.models import DataQualityIssue, BillReport
from admintools.issues import IssueType


def generate_count_report(jur):
    issues = IssueType.get_issues_for('bill')
    counts = {'no_actions_count': 0,
              'no_sponsors_count': 0,
              'no_versions_count': 0,
              'unmatched_person_sponsor_count': 0,
              'unmatched_org_sponsor_count': 0
              }
    for issue in issues:
        issue = IssueType.class_for(issue) + '_' + issue
        count = DataQualityIssue.objects.filter(jurisdiction=jur, issue=issue).count()
        if 'no_actions' in issue:
            counts['no_actions_count'] = count
        elif 'no_sponsors' in issue:
            counts['no_sponsors_count'] = count
        elif 'no_versions' in issue:
            counts['no_versions_count'] = count
        elif 'unmatched_person_sponsor' in issue:
            counts['unmatched_person_sponsor_count'] = count
        else:
            counts['unmatched_org_sponsor_count'] = count
    BillReport.objects.update_or_create(jurisdiction=jur, defaults=counts)
    print("Updated Bill Report for %s" % jur.name)


def bill_report():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        generate_count_report(jur)
