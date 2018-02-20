from opencivicdata.core.models import Organization
from .common import create_issues
from ..issues import IssueType
from ..models import DataQualityIssue


def organizations_report(jur):
    DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                    issue__startswith='organization-'
                                    ).delete()
    count = 0
    issues = IssueType.get_issues_for('organization')
    for issue in issues:
        if issue == 'no-memberships':
            queryset = Organization.objects.filter(
                jurisdiction=jur, memberships__isnull=True).exclude(
                    classification__exact='legislature')
            count += create_issues(queryset, issue, jur)
        else:
            raise ValueError("Organizations Importer needs update for new issue.")
    print("Imported Organization Related {} Issues for {}".format(count, jur.name))
