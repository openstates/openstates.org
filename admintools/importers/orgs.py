from admintools.issues import IssueType
from opencivicdata.core.models import (Jurisdiction, Organization,
                                       Membership, Post)
from admintools.models import DataQualityIssue


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
                posts = Post.objects.filter(organization__jurisdiction=jur)
                queryset = set()
                for post in posts:
                    if Membership.objects.filter(post=post).count() > \
                            post.maximum_memberships:
                            queryset.add(post)
                count += create_org_issues(queryset, issue, jur)
            elif issue == 'few-memberships':
                posts = Post.objects.filter(organization__jurisdiction=jur)
                queryset = set()
                for post in posts:
                    if Membership.objects.filter(post=post).count() < \
                            post.maximum_memberships:
                            queryset.add(post)
                count += create_org_issues(queryset, issue, jur)
            else:
                raise ValueError("Organization Importer needs "
                                 "update for new issue.")
        print("Imported Organization Related {} Issues for {}".format(count,
                                                                      jur.name)
              )
