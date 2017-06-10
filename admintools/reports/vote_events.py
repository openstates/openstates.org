from opencivicdata.core.models import Jurisdiction
from admintools.models import DataQualityIssue, VoteEventReport
from admintools.issues import IssueType


def generate_count_report(jur):
    issues = IssueType.get_issues_for('voteevent')
    counts = {'missing_bill_count': 0,
              'missing_voters_count': 0,
              'missing_counts_count': 0,
              'bad_counts_count': 0,
              'unmatched_voter_count': 0
              }
    for issue in issues:
        issue = IssueType.class_for(issue) + '_' + issue
        count = DataQualityIssue.objects.filter(jurisdiction=jur, issue=issue).count()
        if 'missing_bill' in issue:
            counts['missing_bill_count'] = count
        elif 'missing_voters' in issue:
            counts['missing_voters_count'] = count
        elif 'missing_counts' in issue:
            counts['missing_counts_count'] = count
        elif 'bad_counts' in issue:
            counts['bad_counts_count'] = count
        else:
            counts['unmatched_voter_count'] = count
    VoteEventReport.objects.update_or_create(jurisdiction=jur, defaults=counts)
    print("Updated VoteEvent Report for %s" % jur.name)


def voteevent_report():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        generate_count_report(jur)
