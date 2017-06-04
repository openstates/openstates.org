from admintools.issues import IssueType
from admintools.models import DataQualityIssue
from opencivicdata.legislative.models import VoteEvent
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType


def create_vote_event_issues(queryset, issue):
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


def vote_event_issues():
    for issue in IssueType.get_issues_for('voteevent'):
        if issue == 'missing-bill':
            print("importing vote event with missing bills...")

            queryset = VoteEvent.objects.filter(bill__isnull=True)
            create_vote_event_issues(queryset, issue)

        elif issue == 'unmatched-voter':
            print("importing vote event with unmatched voter...")

            queryset = VoteEvent.objects.filter(votes__isnull=False, votes__voter__isnull=True).distinct()
            create_vote_event_issues(queryset, issue)

        elif issue == 'missing-voters':
            print("importing vote event with missing voters...")

            queryset = VoteEvent.objects.filter(votes__isnull=True)
            create_vote_event_issues(queryset, issue)

        elif issue == 'missing-counts':
            print("importing vote event with missing yes & no votes...")

            queryset = VoteEvent.objects.filter(Q(counts__option='yes',
                                                  counts__value=0)
                                                & Q(counts__option='no',
                                                    counts__value=0))

            create_vote_event_issues(queryset, issue)

        else:
            print("importing vote event with bad votes...")

            queryset = VoteEvent.objects.filter(counts__option='other', counts__value__gt=0)
            create_vote_event_issues(queryset, issue)
