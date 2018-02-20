from ..issues import IssueType
from ..models import DataQualityIssue


def create_issues(queryset, issue, jur):
    obj_list = []
    issue = IssueType.class_for(issue) + '-' + issue
    dqis_list = DataQualityIssue.objects.filter(issue=issue, jurisdiction=jur).values_list(
                                                'object_id', flat=True)
    for query_obj in queryset:
        if query_obj.id not in dqis_list:
            obj_list.append(
                DataQualityIssue(content_object=query_obj, issue=issue, jurisdiction=jur)
            )
    DataQualityIssue.objects.bulk_create(obj_list)
    return len(obj_list)


def create_name_issues(queryset, issue, jur):
    obj_list = []
    issue = IssueType.class_for(issue) + '-' + issue
    name_list = DataQualityIssue.objects.filter(issue=issue, jurisdiction=jur).values_list(
        'unmatched_name', flat=True)

    for query_obj in queryset:
        if query_obj['name'] not in name_list:
            obj_list.append(
                DataQualityIssue(unmatched_name=query_obj['name'], issue=issue, jurisdiction=jur)
            )
    DataQualityIssue.objects.bulk_create(obj_list)
    return len(obj_list)
