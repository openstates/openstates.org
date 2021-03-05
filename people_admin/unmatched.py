import typing
from collections import defaultdict
from django.db.models import Count
from django.contrib.auth.models import User
from openstates.data.models import BillSponsorship, LegislativeSession, PersonVote
from utils.common import abbr_to_jid
from .models import UnmatchedName, NameStatus, DeltaSet, PersonDelta


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


def update_unmatched(abbr: str, session: str) -> int:
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
        UnmatchedName.objects.update_or_create(
            session=session,
            name=name,
            # update numbers, but don't update status/match if it is already set
            defaults=dict(
                sponsorships_count=missing_sponsorships.get(name, 0),
                votes_count=missing_votes.get(name, 0),
            ),
        )
        n += 1
    return n


def unmatched_to_deltas(abbr: str) -> int:
    bot_user, _ = User.objects.get_or_create(username="openstates-bot")

    names = list(
        UnmatchedName.objects.filter(
            session__jurisdiction_id=abbr_to_jid(abbr),
            status=NameStatus.MATCHED_PERSON,
            matched_person_id__isnull=False,
        )
    )

    # bail without any work if there aren't names to consider
    if not names:
        return 0

    delta_set, created = DeltaSet.objects.get_or_create(
        name=f"{abbr.upper()} legislator matching", pr_url="", created_by=bot_user,
    )
    delta_set.person_deltas.all().delete()

    # build list of changes for each person
    person_changes = defaultdict(list)
    for name in names:
        person_changes[name.matched_person_id].append(
            ["append", "other_names", {"name": name.name}]
        )

    for person_id, changes in person_changes.items():
        PersonDelta.objects.create(
            person_id=person_id, delta_set=delta_set, data_changes=changes
        )
    return len(person_changes)
