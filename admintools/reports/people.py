from opencivicdata.core.models import Jurisdiction
from admintools.models import DataQualityIssue, PeopleReport
from admintools.issues import IssueType


def generate_count_report(jur):
    issues = IssueType.get_issues_for('person')
    counts = {'missing_phone_count': 0,
              'missing_email_count': 0,
              'missing_photo_count': 0,
              'missing_address_count': 0
              }
    for issue in issues:
        issue = IssueType.class_for(issue) + '_' + issue
        count = DataQualityIssue.objects.filter(jurisdiction=jur, issue=issue).count()
        if 'phone' in issue:
            counts['missing_phone_count'] = count
        elif 'email' in issue:
            counts['missing_email_count'] = count
        elif 'photo' in issue:
            counts['missing_photo_count'] = count
        else:
            counts['missing_address_count'] = count
    PeopleReport.objects.update_or_create(jurisdiction=jur, defaults=counts)
    print("Updated People Report for %s" % jur.name)


def people_report():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        generate_count_report(jur)
