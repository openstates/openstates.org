from admintools.issues import IssueType
from opencivicdata.core.models import (Jurisdiction, Organization,
                                       Membership, Post)
from admintools.models import DataQualityIssue
from django.db.models import Count, F, Q
from django.contrib.contenttypes.models import ContentType
from .common import create_issues


def orgs_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    org_contenttype_obj = ContentType.objects.get_for_model(Organization)
    mem_contenttype_obj = ContentType.objects.get_for_model(Membership)
    post_contenttype_obj = ContentType.objects.get_for_model(Post)
    for jur in all_jurs:
        DataQualityIssue.objects.filter(jurisdiction=jur, status='active'
                                        ).filter(
                                        Q(content_type=org_contenttype_obj)
                                        | Q(content_type=mem_contenttype_obj)
                                        | Q(content_type=post_contenttype_obj)
                                        ).delete()
        count = 0
        issues = IssueType.get_issues_for('organization') + \
            IssueType.get_issues_for('membership') + \
            IssueType.get_issues_for('post')
        for issue in issues:
            if issue == 'no-memberships':
                queryset = Organization.objects \
                        .filter(jurisdiction=jur, memberships__isnull=True) \
                        .exclude(classification__exact='legislature')
                count += create_issues(queryset, issue, jur)

            elif issue == 'unmatched-person':
                queryset = Membership.objects \
                    .filter(organization__jurisdiction=jur,
                            person__isnull=True)
                count += create_issues(queryset, issue, jur)
            elif issue == 'many-memberships':
                queryset = Post.objects.filter(
                    organization__jurisdiction=jur).annotate(
                        num=Count('memberships')).filter(
                            num__gt=F('maximum_memberships'))
                count += create_issues(queryset, issue, jur)
            elif issue == 'few-memberships':
                queryset = Post.objects.filter(
                    organization__jurisdiction=jur).annotate(
                        num=Count('memberships')).filter(
                            num__lt=F('maximum_memberships'))
                count += create_issues(queryset, issue, jur)
            else:
                raise ValueError("Organization Importer needs "
                                 "update for new issue.")
        print("Imported Organization Related {} Issues for {}".format(count,
                                                                      jur.name)
              )
