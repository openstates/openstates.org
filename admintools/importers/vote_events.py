from admintools.models import DataQualityIssues
from opencivicdata.legislative.models import VoteEvent
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType


def create_vote_event_issues(queryset, issue, alert):
    obj_list = []
    for query_obj in queryset:
        contenttype_obj = ContentType.objects.get_for_model(query_obj)
        if not DataQualityIssues.objects.filter(object_id=query_obj.id,
                                                content_type=contenttype_obj,
                                                alert=alert, issue=issue):
            obj_list.append(
                DataQualityIssues(content_object=query_obj,
                                  alert=alert,
                                  issue=issue
                                  )
            )
    print("Found New Issues: {}".format(len(obj_list)))
    DataQualityIssues.objects.bulk_create(obj_list)


def vote_event_issues():
    issues = ['voteevent_missing_bill',
              'unmatched_voter',
              'missing_voters',
              'missing_votes',
              'bad_votes']

    for issue in issues:
        if issue == 'voteevent_missing_bill':
            print("importing vote event with missing bills...")

            queryset = VoteEvent.objects.filter(bill__isnull=True)
            create_vote_event_issues(queryset, issue, alert='error')

        elif issue == 'unmatched_voter':
            print("importing vote event with unmatched voter...")

            queryset = VoteEvent.objects.filter(votes__isnull=False, votes__voter__isnull=True).distinct()
            create_vote_event_issues(queryset, issue, alert='warning')

        elif issue == 'missing_voters':
            print("importing vote event with missing voters...")

            queryset = VoteEvent.objects.filter(votes__isnull=True)
            create_vote_event_issues(queryset, issue, alert='error')

        elif issue == 'missing_votes':
            print("importing vote event with missing yes & no votes...")

            queryset = VoteEvent.objects.filter(Q(counts__option='yes',
                                                  counts__value=0)
                                                & Q(counts__option='no',
                                                    counts__value=0))

            create_vote_event_issues(queryset, issue, alert='error')

        else:
            print("importing vote event with bad votes...")

            queryset = VoteEvent.objects.filter(counts__option='other', counts__value__gt=0)
            create_vote_event_issues(queryset, issue, alert='warning')
