import uuid
from utils.common import (
    jid_to_abbr,
    abbr_to_jid,
    encode_uuid,
    decode_uuid,
    sessions_with_bills,
)
from openstates.data.models import Division, Jurisdiction, Bill


def test_jid_to_abbr():
    assert jid_to_abbr("ocd-jurisdiction/country:us/state:nc/government") == "nc"


def test_abbr_to_jid():
    assert abbr_to_jid("nc") == "ocd-jurisdiction/country:us/state:nc/government"
    assert abbr_to_jid("dc") == "ocd-jurisdiction/country:us/district:dc/government"
    assert abbr_to_jid("pr") == "ocd-jurisdiction/country:us/territory:pr/government"


def test_encode_decode_uuid():
    person_id = "ocd-person/" + str(uuid.uuid4())
    assert decode_uuid(encode_uuid(person_id)) == person_id


def test_sessions_with_bills():
    jid = "ocd-jurisdiction/country:us/state:wi/government"

    d = Division.objects.create(id="ocd-division/country:us/state:wi", name="Wisconsin")
    j = Jurisdiction.objects.create(id=jid, name="Wisconsin", division=d)
    j.legislative_sessions.create(identifier="2016", name="2016")
    s17 = j.legislative_sessions.create(identifier="2017", name="2017")
    s18 = j.legislative_sessions.create(identifier="2018", name="2018")
    Bill.objects.create(identifier="HB 1", title="Test", legislative_session=s17)
    Bill.objects.create(identifier="HB 1", title="Test", legislative_session=s18)
    Bill.objects.create(identifier="HB 2", title="Test", legislative_session=s18)

    sessions = sessions_with_bills(jid)
    assert len(sessions) == 2
    assert s17 in sessions
    assert s18 in sessions


# TODO: test pretty_url
