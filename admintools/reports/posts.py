from admintools.issues import IssueType
from opencivicdata.core.models import Jurisdiction, Post
from django.db.models import Count, F
from .common import create_issues


def posts_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        count = 0
        issues = IssueType.get_issues_for('post')
        for issue in issues:
            if issue == 'many-memberships':
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
                raise ValueError("Posts Importer needs "
                                 "update for new issue.")
        print("Imported Post Related {} Issues for {}".format(count, jur.name)
              )
