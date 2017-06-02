from opencivicdata.core.models import Person
from admintools.models import DataQualityIssues


def create_person_issues(queryset, issue):
    obj_list = []
    for query_obj in queryset:
        obj_list.append(
            DataQualityIssues(content_object=query_obj,
                              alert='warning',
                              issue=issue
                              )
        )
    DataQualityIssues.objects.bulk_create(obj_list)


def person_issues():
    issues = ['email', 'address', 'voice', 'image']
    for issue in issues:
        if issue in ['email', 'address', 'voice']:
            print("importing person with missing %s..." % issue)

            queryset = Person.objects.exclude(contact_details__type=issue)
            create_person_issues(queryset, issue)
        else:
            print("importing person with missing %s..." % issue)
            
            queryset = Person.objects.filter(image__exact='')
            create_person_issues(queryset, issue)
