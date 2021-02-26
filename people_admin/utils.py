import typing
from django.db.models import Count
from openstates.data.models import BillSponsorship, LegislativeSession, PersonVote
from utils.common import abbr_to_jid
from .models import UnmatchedName


def check_sponsorships(session: LegislativeSession) -> typing.Dict[str, int]:
    unmatched = (
        BillSponsorship.objects.filter(
            bill__legislative_session=session, person=None, organization=None,
        )
        .values("name")
        .annotate(count=Count("id"))
    )

    return {u["name"]: u["count"] for u in unmatched}


def check_votes(session: LegislativeSession) -> typing.Dict[str, int]:
    unmatched = (
        PersonVote.objects.filter(
            vote_event__bill__legislative_session=session, voter=None,
        )
        .values("voter_name")
        .annotate(count=Count("id"))
    )

    return {u["voter_name"]: u["count"] for u in unmatched}


def update_unmatched(abbr: str, session: str,) -> int:
    session = LegislativeSession.objects.get(
        jurisdiction_id=abbr_to_jid(abbr), identifier=session
    )

    missing_sponsorships = check_sponsorships(session)
    missing_votes = check_votes(session)

    all_names = set(missing_sponsorships) | set(missing_votes)

    # delete rows that no longer exist
    UnmatchedName.objects.filter(session=session).exclude(name__in=all_names).delete()

    n = 0

    for name in all_names:
        UnmatchedName.objects.create(
            session=session,
            name=name,
            sponsorships_count=missing_sponsorships.get(name, 0),
            votes_count=missing_votes.get(name, 0),
        )
        n += 1
    return n
