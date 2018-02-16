from ..issues import IssueType
from ..models import DataQualityIssue


def create_issues(queryset, issue, jur):
    obj_list = []
    alert = IssueType.level_for(issue)
    issue = IssueType.class_for(issue) + '-' + issue
    dqis_list = DataQualityIssue.objects.filter(alert=alert, issue=issue,
                                                jurisdiction=jur).values_list(
                                                'object_id', flat=True)
    for query_obj in queryset:
        if query_obj.id not in dqis_list:
            obj_list.append(
                DataQualityIssue(content_object=query_obj, alert=alert,
                                 issue=issue, jurisdiction=jur,
                                 status='active')
            )
    DataQualityIssue.objects.bulk_create(obj_list)
    return len(obj_list)
