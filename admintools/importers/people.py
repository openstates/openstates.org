from admintools.issues import IssueType
from opencivicdata.core.models import Jurisdiction, Person
from admintools.models import DataQualityIssue


def create_person_issues(queryset, issue, jur):
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


def person_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                        issue__startswith='person-').delete()
        count = 0
        people = Person.objects.filter(
            memberships__organization__jurisdiction=jur).distinct()
        for issue in IssueType.get_issues_for('person'):
            if issue == 'missing-photo':
                queryset = people.filter(image__exact='')
                count += create_person_issues(queryset, issue, jur)
            elif issue == 'missing-phone':
                queryset = people.exclude(contact_details__type='voice')
                count += create_person_issues(queryset, issue, jur)
            elif issue in ['missing-email', 'missing-address']:
                queryset = people.exclude(contact_details__type=issue[8:])
                count += create_person_issues(queryset, issue, jur)
            else:
                raise ValueError("People Importer needs update for new issue.")
        print("Imported People Related {} Issues for {}".format(count,
                                                                jur.name))
