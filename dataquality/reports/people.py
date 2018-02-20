from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F
from opencivicdata.core.models import Person, Membership, Post
from .common import create_issues, create_name_issues
from ..issues import IssueType
from ..models import DataQualityIssue


def people_report(jur):
    contenttype_obj = ContentType.objects.get_for_model(Person)
    DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                    content_type=contenttype_obj).delete()
    count = 0
    people = Person.objects.filter(memberships__organization__jurisdiction=jur).distinct()
    for issue in IssueType.get_issues_for('person'):
        if issue == 'missing-photo':
            queryset = people.filter(image__exact='')
            count += create_issues(queryset, issue, jur)
        elif issue == 'missing-phone':
            queryset = people.exclude(contact_details__type='voice')
            count += create_issues(queryset, issue, jur)
        elif issue in ['missing-email', 'missing-address']:
            queryset = people.exclude(contact_details__type=issue[8:])
            count += create_issues(queryset, issue, jur)
        else:
            raise ValueError("People Importer needs update for new issue.")
    print("Imported People Related {} Issues for {}".format(count, jur.name))


def memberships_report(jur):
    mem_contenttype_obj = ContentType.objects.get_for_model(Membership)
    DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                    content_type=mem_contenttype_obj
                                    ).delete()
    count = 0
    issues = IssueType.get_issues_for('membership')
    for issue in issues:
        if issue == 'unmatched-person':
            queryset = Membership.objects.filter(organization__jurisdiction=jur,
                                                 person__isnull=True).values(name=F('person_name')
                                                                             ).annotate(
                                                     num=Count('name')
                                                 )
            count += create_name_issues(queryset, issue, jur)
        else:
            raise ValueError("Memberships Importer needs update for new issue.")
    print("Imported Memberships Related {} Issues for {}".format(count, jur.name))


def posts_report(jur):
    count = 0
    issues = IssueType.get_issues_for('post')
    for issue in issues:
        if issue == 'many-memberships':
            queryset = Post.objects.filter(organization__jurisdiction=jur).annotate(
                num=Count('memberships')).filter(num__gt=F('maximum_memberships'))
            count += create_issues(queryset, issue, jur)
        elif issue == 'few-memberships':
            queryset = Post.objects.filter(
                organization__jurisdiction=jur).annotate(num=Count('memberships')).filter(
                    num__lt=F('maximum_memberships'))
            count += create_issues(queryset, issue, jur)
        else:
            raise ValueError("Posts Importer needs update for new issue.")
    print("Imported Post Related {} Issues for {}".format(count, jur.name))
