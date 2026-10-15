import json
import zipfile
import pytest
from openstates.data.models import VoteEvent
from graphapi.tests.utils import populate_db
from bulk.management.commands.bulk_export import export_session_json


@pytest.mark.django_db
def test_session_json_includes_vote_ids():
    populate_db()
    filename = export_session_json("ak", "2018")
    with zipfile.ZipFile(filename) as zf:
        bills = json.loads(zf.read("ak/2018/ak_2018_bills.json"))
    vote_ids = [v["id"] for b in bills for v in b["votes"]]
    assert vote_ids
    assert sorted(vote_ids) == sorted(
        VoteEvent.objects.filter(bill__id__in=[b["id"] for b in bills]).values_list(
            "id", flat=True
        )
    )
