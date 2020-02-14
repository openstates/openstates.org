from functools import lru_cache
from collections import defaultdict
from django.core.management.base import BaseCommand
from opencivicdata.legislative.models import Bill
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
def get_item_properties(bill_id):
    return {
        "jurisdiction_id": Bill.objects.get(
            pk=bill_id
        ).legislative_session.jurisdiction_id,
        "session_id": Bill.objects.get(pk=bill_id).legislative_session.identifier,
    }


def accumulate_changes(changes):
    """
    roll up all changes in a list to be attached to the appropriate ID
    """
    # for each type, we return a dict mapping ids to change objects
    accum = {
        "bill": defaultdict(list),
        "vote": defaultdict(list),
        "related_entity": defaultdict(list),
        "version_link": defaultdict(list),
        "document_link": defaultdict(list),
    }

    for c in changes:
        if c.object_id.startswith("ocd-bill"):
            ctype = "bill"
        elif c.object_id.startswith("ocd-vote"):
            ctype = "vote"
        elif c.table_name == "opencivicdata_billactionrelatedentity":
            ctype = "related_entity"
        elif c.table_name == "opencivicdata_billversionlink":
            ctype = "version_link"
        elif c.table_name == "opencivicdata_billdocumentlink":
            ctype = "document_link"
        else:
            raise ValueError("unexpected id: " + c.object_id)
        accum[ctype][c.object_id].append(c)
    return accum


MAPPING = {
    "opencivicdata_billaction": "actions",
    "opencivicdata_billversion": "versions",
    "opencivicdata_billdocument": "documents",
    "opencivicdata_billsponsorship": "sponsors",
    "opencivicdata_billsource": "sources",
    "opencivicdata_billabstract": "abstracts",
}


def update_old(old, change):
    """ like dict.update, but keeps first value it sees """
    for k, v in change.items():
        if k not in old:
            old[k] = v


def clean_subobj(subobj):
    """ we don't want to show these since we're just nesting the objects """
    subobj.pop("id")
    subobj.pop("bill_id")
    return subobj


def make_change_object(changes):
    """
        changes is a list of changes that are for the same object

        return a single object representing all changes as one
    """
    # start with the the parent object id
    item_id = changes[0].object_id
    # unless we see a top-level create or delete, this is an update
    change_type = "update"
    old_obj = {}
    new_obj = {}

    for change in changes:
        if (
            change.table_name == "opencivicdata_bill"
            or change.table_name == "opencivicdata_vote"
        ):
            if change.change_type == "update":
                update_old(old_obj, change.old)
                new_obj.update(change.new)
            elif change.change_type == "create":
                new_obj.update(change.new)
                change_type = "create"
            elif change.change_type == "delete":
                change_type = "delete"
                old_obj = change.old
            else:
                raise ValueError(change.change_type)
        else:
            # standard subfield handling
            field_name = MAPPING[change.table_name]

            if field_name not in new_obj:
                new_obj[field_name] = []
                old_obj[field_name] = []

            # subfields are either deleted or created, updates don't currently happen via pupa
            if change.change_type == "delete":
                old_obj[field_name].append(clean_subobj(change.old))
            elif change.change_type == "create":
                new_obj[field_name].append(clean_subobj(change.new))
            else:
                print(change.object_id, change.change_type, field_name, change.new)
                raise ValueError("update unexpected")

    return {
        "item_type": "bill",
        "item_id": item_id,
        "item_properties": get_item_properties(item_id),
        "action": change_type,
        "changes": {"old": old_obj, "new": new_obj},
    }


def handle_epoch(**kwargs):
    """
    get all changes for a time period and return list of change_objects
    """
    changes = list(Change.objects.filter(**kwargs))
    formatted = format_time(**kwargs)
    print(f"{len(changes)} changes for {formatted}")
    changes = accumulate_changes(changes)
    print(f"{len(changes['bill'])} bills, {len(changes['vote'])} votes")

    # TODO: handle votes
    # TODO: handle subobjects
    for bill_id, changes in changes["bill"].items():
        change_obj = make_change_object(changes)
        from pprint import pprint

        pprint(change_obj)


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
