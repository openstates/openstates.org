from collections import defaultdict
from opencivicdata.core.models import Person
from admintools.models import DataQualityIssues
from django.contrib.contenttypes.models import ContentType


def create_person_issues(queryset, issue):
    for query_obj in queryset:
        # TODO any way to use bulk_create with get ?
        contenttype_obj = ContentType.objects.get_for_model(query_obj)
        if not DataQualityIssues.objects.filter(object_id=query_obj.id, content_type=contenttype_obj):
            DataQualityIssues.objects.create(content_object=query_obj,
                                             alert='warning',
                                             issue=issue
                                             )


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
