from functools import lru_cache
from collections import defaultdict
from django.core.management.base import BaseCommand
from opencivicdata.legislative.models import Bill, VoteEvent
from history.models import Change


def format_time(
    event_time__year,
    event_time__month,
    event_time__day,
    event_time__hour=None,
    event_time__minute=None,
):
    timestr = f"{event_time__year}-{event_time__month:02d}-{event_time__day:02d}"
    if event_time__hour:
        timestr += f"T{event_time__hour:02d}"
    if event_time__minute:
        timestr += f":{event_time__minute:02d}"
    return timestr


@lru_cache()
def get_bill(bill_id):
    return Bill.objects.get(pk=bill_id)


@lru_cache()
def get_vote(vote_id):
    return VoteEvent.objects.get(pk=vote_id)


def accumulate_changes(changes):
    bill_changes = defaultdict(list)
    vote_changes = defaultdict(list)

    for c in changes:
        if c.object_id.startswith("ocd-bill"):
            bill_changes[c.object_id].append(c)
        elif c.object_id.startswith("ocd-vote"):
            vote_changes[c.object_id].append(c)
        else:
            raise ValueError("unexpected id: " + c.object_id)

    return bill_changes, vote_changes


MAPPING = {
    "opencivicdata_billaction": "actions",
}


def update_old(old, change):
    """ like dict.update, but keeps first value it sees """
    for k, v in change.items():
        if k not in old:
            old[k] = v


def clean_subobj(subobj):
    subobj.pop("id")
    subobj.pop("bill_id")
    return subobj


def make_change_object(changes):
    old_obj = {}
    change_obj = {}

    for change in changes:
        if change.table_name == "opencivicdata_bill":
            if change.change_type == "update":
                update_old(old_obj, change.old)
                change_obj.update(change.new)
            else:
                raise ValueError("not handled")
        else:
            field_name = MAPPING[change.table_name]
            if field_name not in change_obj:
                change_obj[field_name] = []
                old_obj[field_name] = []
            if change.change_type == "delete":
                old_obj[field_name].append(clean_subobj(change.old))
            elif change.change_type == "create":
                change_obj[field_name].append(clean_subobj(change.new))
            else:
                print(change.object_id, change.change_type, field_name, change.new)
                raise ValueError("update unexpected")

    from pprint import pprint

    pprint(old_obj)
    pprint(change_obj)


def handle_epoch(**kwargs):
    changes = list(Change.objects.filter(**kwargs))
    formatted = format_time(**kwargs)
    print(f"{len(changes)} changes for {formatted}")
    bill_changes, vote_changes = accumulate_changes(changes)
    print(f"processed into {len(bill_changes)} bills and {len(vote_changes)} votes")

    for bill_id, changes in bill_changes.items():
        make_change_object(changes)


class Command(BaseCommand):
    help = "export history data"

    def handle(self, *args, **options):
        for time in Change.objects.values(
            "event_time__year",
            "event_time__month",
            "event_time__day",
            "event_time__hour",
            "event_time__minute",
        ).distinct():
            handle_epoch(**time)
            break
