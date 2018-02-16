from django.contrib.contenttypes.models import ContentType
from opencivicdata.legislative.models import VoteEvent, VoteCount, PersonVote
from .common import create_issues
from ..issues import IssueType
from ..models import DataQualityIssue


def vote_events_report(jur):
    contenttype_obj = ContentType.objects.get_for_model(VoteEvent)
    DataQualityIssue.objects.filter(jurisdiction=jur, status='active',
                                    content_type=contenttype_obj
                                    ).delete()
    voteevents = VoteEvent.objects.filter(legislative_session__jurisdiction=jur)
    count = 0
    for issue in IssueType.get_issues_for('voteevent'):
        if issue == 'missing-bill':
            queryset = voteevents.filter(bill__isnull=True)
            count += create_issues(queryset, issue, jur)

        elif issue == 'unmatched-voter':
            queryset = voteevents.filter(votes__isnull=False,
                                         votes__voter__isnull=True).distinct()
            count += create_issues(queryset, issue, jur)

        elif issue == 'missing-voters':
            queryset = voteevents.filter(votes__isnull=True)
            count += create_issues(queryset, issue, jur)

        elif issue == 'missing-counts':
            queryset = voteevents.filter(counts__option='yes',
                                         counts__value=0).filter(counts__option='no',
                                                                 counts__value=0)
            count += create_issues(queryset, issue, jur)

        elif issue == 'bad-counts':
            all_counts = VoteCount.objects.filter(
                vote_event__legislative_session__jurisdiction=jur)
            queryset = set()
            for _count in all_counts:
                if PersonVote.objects.filter(vote_event=_count.vote_event,
                                             option=_count.option).count() != _count.value:
                    queryset.add(_count.vote_event)
            count += create_issues(queryset, issue, jur)
        else:
            raise ValueError("VoteEvents Importer needs update for new issue.")
    print("Imported VoteEvents Related {} Issues for {}".format(count, jur.name))
