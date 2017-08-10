from admintools.issues import IssueType
from opencivicdata.core.models import (Jurisdiction, Organization,
                                       Membership, Post)
from admintools.models import DataQualityIssue
from django.db.models import Count, F, Q


def create_org_issues(queryset, issue, jur):
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


def orgs_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        DataQualityIssue.objects.filter(jurisdiction=jur, status='active'
                                        ).filter(
                                        Q(issue__startswith='organization-')
                                        | Q(issue__startswith='membership-')
                                        | Q(issue__startswith='post-')
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
                count += create_org_issues(queryset, issue, jur)

            elif issue == 'unmatched-person':
                queryset = Membership.objects \
                    .filter(organization__jurisdiction=jur,
                            person__isnull=True)
                count += create_org_issues(queryset, issue, jur)
            elif issue == 'many-memberships':
                queryset = Post.objects.filter(
                    organization__jurisdiction=jur).annotate(
                        num=Count('memberships')).filter(
                            num__gt=F('maximum_memberships'))
                count += create_org_issues(queryset, issue, jur)
            elif issue == 'few-memberships':
                queryset = Post.objects.filter(
                    organization__jurisdiction=jur).annotate(
                        num=Count('memberships')).filter(
                            num__lt=F('maximum_memberships'))
                count += create_org_issues(queryset, issue, jur)
            else:
                raise ValueError("Organization Importer needs "
                                 "update for new issue.")
        print("Imported Organization Related {} Issues for {}".format(count,
                                                                      jur.name)
              )
