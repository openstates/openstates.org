from collections import defaultdict
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
    issues = defaultdict(list)
    # we may want to extend this list later.
    issues['contact_issues'] = ['email', 'address', 'voice']
    issues['other_issues'] = ['image']
    for issues_type, issues in issues.items():
        if issues_type == 'contact_issues':
            for issue in issues:
                queryset = Person.objects.exclude(contact_details__type=issue)
                create_person_issues(queryset, issue)
        else:
            for issue in issues:
                queryset = Person.objects.filter(image__exact='')
                create_person_issues(queryset, issue)
