from admintools.issues import IssueType
from opencivicdata.core.models import Jurisdiction, Membership
from admintools.models import DataQualityIssue
from django.contrib.contenttypes.models import ContentType
from .common import create_issues


def memberships_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    mem_contenttype_obj = ContentType.objects.get_for_model(Membership)
    for jur in all_jurs:
        DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                        content_type=mem_contenttype_obj
                                        ).delete()
        count = 0
        issues = IssueType.get_issues_for('membership')
        for issue in issues:
            if issue == 'unmatched-person':
                queryset = Membership.objects \
                    .filter(organization__jurisdiction=jur,
                            person__isnull=True)
                count += create_issues(queryset, issue, jur)
            else:
                raise ValueError("Memberships Importer needs "
                                 "update for new issue.")
        print("Imported Memberships Related {} Issues for {}".format(count,
                                                                     jur.name)
              )
