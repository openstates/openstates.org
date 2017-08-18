from admintools.issues import IssueType
from opencivicdata.core.models import Jurisdiction, Person
from admintools.models import DataQualityIssue
from django.contrib.contenttypes.models import ContentType
from .common import create_issues


def people_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    contenttype_obj = ContentType.objects.get_for_model(Person)
    for jur in all_jurs:
        DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                        content_type=contenttype_obj).delete()
        count = 0
        people = Person.objects.filter(
            memberships__organization__jurisdiction=jur).distinct()
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
        print("Imported People Related {} Issues for {}".format(count,
                                                                jur.name))
