from admintools.issues import IssueType
from opencivicdata.core.models import Person
from admintools.models import DataQualityIssue
from django.contrib.contenttypes.models import ContentType


def create_person_issues(queryset, issue):
    obj_list = []
    alert = IssueType.level_for(issue)
    issue = IssueType.class_for(issue) + '-' + issue
    for query_obj in queryset:
        contenttype_obj = ContentType.objects.get_for_model(query_obj)
        if not DataQualityIssue.objects.filter(object_id=query_obj.id,
                                               content_type=contenttype_obj,
                                               alert=alert, issue=issue):
            obj_list.append(
                DataQualityIssue(content_object=query_obj, alert=alert,
                                 issue=issue)
            )
    print("Found New Issues: {}".format(len(obj_list)))
    DataQualityIssue.objects.bulk_create(obj_list)


def person_issues():
    for issue in IssueType.get_issues_for('person'):
        print("importing person with %s..." % issue)

        if issue == 'missing-photo':
            queryset = Person.objects.filter(image__exact='')
            create_person_issues(queryset, issue)

        elif issue == 'missing-phone':
            queryset = Person.objects.exclude(contact_details__type='voice')
            create_person_issues(queryset, issue)

        else:
            queryset = Person.objects.exclude(contact_details__type=issue[8:])
            create_person_issues(queryset, issue)
