from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from opencivicdata.legislative.models import Bill, BillSponsorship
from .common import create_issues, create_name_issues
from ..issues import IssueType
from ..models import DataQualityIssue


def bills_report(jur):
    contenttype_obj = ContentType.objects.get_for_model(Bill)
    DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                    content_type=contenttype_obj).delete()
    bills = Bill.objects.filter(legislative_session__jurisdiction=jur)
    count = 0
    for issue in IssueType.get_issues_for('bill'):
        if issue == 'no-actions':
            queryset = bills.filter(actions__isnull=True)
            count += create_issues(queryset, issue, jur)
        elif issue == 'no-sponsors':
            queryset = bills.filter(sponsorships__isnull=True)
            count += create_issues(queryset, issue, jur)
        elif issue == 'no-versions':
            queryset = bills.filter(versions__isnull=True)
            count += create_issues(queryset, issue, jur)
        elif issue == 'unmatched-person-sponsor':
            queryset = BillSponsorship.objects.filter(
                bill__legislative_session__jurisdiction=jur,
                entity_type='person',
                person_id=None
            ).values('name').annotate(num=Count('name'))
            count += create_name_issues(queryset, issue, jur)
        elif issue == 'unmatched-org-sponsor':
            queryset = BillSponsorship.objects.filter(
                bill__legislative_session__jurisdiction=jur,
                entity_type='organization',
                organization_id=None
            ).values('name').annotate(num=Count('name'))
            count += create_name_issues(queryset, issue, jur)
        else:
            raise ValueError("Bill Importer needs update for new issue.")
    print("Imported Bills Related {} Issues for {}".format(count, jur.name))
