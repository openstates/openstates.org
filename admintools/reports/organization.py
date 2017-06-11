from opencivicdata.core.models import Jurisdiction
from admintools.models import DataQualityIssue, OrganizationReport
from admintools.issues import IssueType


def generate_count_report(jur):
    issues = IssueType.get_issues_for('organization') + IssueType.get_issues_for('membership')
    counts = {'unmatched_person_count': 0,
              'no_memberships_count': 0}
    for issue in issues:
        issue = IssueType.class_for(issue) + '-' + issue
        count = DataQualityIssue.objects.filter(jurisdiction=jur, issue=issue).count()
        if issue == 'organization-no-memberships':
            counts['no_memberships_count'] = count
        else:
            counts['unmatched_person_count'] = count
    OrganizationReport.objects.update_or_create(jurisdiction=jur, defaults=counts)
    print("Updated Organization Report for %s" % jur.name)


def orgs_report():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        generate_count_report(jur)
