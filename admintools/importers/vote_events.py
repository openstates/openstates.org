from admintools.issues import IssueType
from admintools.models import DataQualityIssue
from opencivicdata.core.models import Jurisdiction
from opencivicdata.legislative.models import VoteEvent
from django.db.models import Q


def create_vote_event_issues(queryset, issue, jur):
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


def vote_event_issues():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        voteevents = VoteEvent.objects.filter(
            legislative_session__jurisdiction=jur)
        count = 0
        for issue in IssueType.get_issues_for('voteevent'):
            if issue == 'missing-bill':
                queryset = voteevents.filter(bill__isnull=True)
                count += create_vote_event_issues(queryset, issue, jur)

            elif issue == 'unmatched-voter':
                queryset = voteevents.filter(votes__isnull=False,
                                             votes__voter__isnull=True) \
                                             .distinct()
                count += create_vote_event_issues(queryset, issue, jur)

            elif issue == 'missing-voters':
                queryset = voteevents.filter(votes__isnull=True)
                count += create_vote_event_issues(queryset, issue, jur)

            elif issue == 'missing-counts':
                queryset = voteevents.filter(Q(counts__option='yes',
                                               counts__value=0)
                                             & Q(counts__option='no',
                                                 counts__value=0))

                count += create_vote_event_issues(queryset, issue, jur)

            else:
                queryset = voteevents.filter(counts__option='other',
                                             counts__value__gt=0)
                count += create_vote_event_issues(queryset, issue, jur)
        print("Imported VoteEvents Related {} Issues for {}".format(count,
                                                                    jur.name))
