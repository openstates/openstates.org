import datetime
from django.db.models import Q
from .common import jid_to_abbr


def get_current_role(person):
    today = datetime.date.today().strftime("%Y-%m-%d")
    party = None
    post = None
    state = None
    chamber = None

    # assume that this person object was fetched with appropriate
    # related data, if not this can get expensive
    for membership in person.memberships.all():
        if not membership.end_date or membership.end_date > today:
            if membership.organization.classification == "party":
                party = membership.organization.name
            elif membership.organization.classification in (
                "upper",
                "lower",
                "legislature",
            ):
                chamber = membership.organization.classification
                state = jid_to_abbr(membership.organization.jurisdiction_id)
                post = membership.post

    return {
        "party": party,
        "chamber": chamber,
        "state": state,
        "district": post.label if post else "",
        "division_id": post.division_id if post else "",
        "role": post.role if post else "",
    }


def current_role_filters():
    today = datetime.date.today().isoformat()
    return [Q(memberships__start_date='') | Q(memberships__start_date__lte=today),
            Q(memberships__end_date='') | Q(memberships__end_date__gte=today)]
