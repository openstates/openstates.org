from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F, Subquery, OuterRef, Q
from opencivicdata.legislative.models import VoteEvent, VoteCount, PersonVote
from .common import create_issues, create_name_issues
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
            queryset = PersonVote.objects.filter(
                vote_event__legislative_session__jurisdiction=jur,
                voter__isnull=True).values(name=F('voter_name')).annotate(num=Count('voter_name'))
            count += create_name_issues(queryset, issue, jur)

        elif issue == 'missing-voters':
            queryset = voteevents.filter(votes__isnull=True)
            count += create_issues(queryset, issue, jur)

        elif issue == 'missing-counts':
            queryset = voteevents.filter(counts__option='yes',
                                         counts__value=0).filter(counts__option='no',
                                                                 counts__value=0)
            count += create_issues(queryset, issue, jur)

        elif issue == 'bad-counts':
            queryset = voteevents.annotate(
                yes_sum=Count('pk', filter=Q(votes__option='yes')),
                no_sum=Count('pk', filter=Q(votes__option='no')),
                other_sum=Count('pk', filter=Q(votes__option='other')),
                yes_count=Subquery(VoteCount.objects.filter(vote_event=OuterRef('pk'),
                                                            option='yes').values('value')),
                no_count=Subquery(VoteCount.objects.filter(vote_event=OuterRef('pk'),
                                                           option='no').values('value')),
                other_count=Subquery(VoteCount.objects.filter(vote_event=OuterRef('pk'),
                                                              option='other').values('value')),
            )
            bad_counts = []
            for vote in queryset:
                if (vote.yes_sum != vote.yes_count or
                        vote.no_sum != vote.no_sum or
                        vote.other_sum != vote.other_sum):
                    bad_counts.append(vote)
            count += create_issues(bad_counts, issue, jur)
        else:
            raise ValueError("VoteEvents Importer needs update for new issue.")
    print("Imported VoteEvents Related {} Issues for {}".format(count, jur.name))
