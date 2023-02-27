from utils.orgs import get_chambers_from_abbr, get_legislature_from_abbr


def test_get_chambers():
    chambers = get_chambers_from_abbr("ak")
    assert len(chambers) == 2
    assert {"upper", "lower"} == {c.classification for c in chambers}


def test_get_legislature():
    assert get_legislature_from_abbr("ak").name == "Alaska Legislature"
