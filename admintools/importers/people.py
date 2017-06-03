from opencivicdata.core.models import Person
from admintools.models import DataQualityIssues


def create_person_issues(queryset, issue, alert):
    obj_list = []
    for query_obj in queryset:
        if not DataQualityIssues.objects.filter(related_ids__contains=[query_obj.id],
                                                alert=alert, issue=issue):
            obj_list.append(
                DataQualityIssues(related_ids=[query_obj.id],
                                  alert=alert,
                                  issue=issue
                                  )
            )
    print("Found New Issues: {}".format(len(obj_list)))
    DataQualityIssues.objects.bulk_create(obj_list)


def person_issues():
    issues = ['email', 'address', 'voice', 'image']
    for issue in issues:
        print("importing person with missing %s..." % issue)

        if issue == 'image':
            queryset = Person.objects.filter(image__exact='')
            create_person_issues(queryset, issue, alert='warning')
        else:
            queryset = Person.objects.exclude(contact_details__type=issue)
            create_person_issues(queryset, issue, alert='warning')
