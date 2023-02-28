from utils.cli import yield_state_sessions


def test_yield_state_sessions_simplest():
    results = list(yield_state_sessions("ks", "2020"))
    assert results == [("ks", "2020")]


def test_yield_state_sessions_one_state(sessions):
    results = list(yield_state_sessions("ks", None))
    assert results == [("ks", "2019"), ("ks", "2020")]


def test_yield_state_sessions_all_state(sessions):
    # just the latest session for each state
    results = list(yield_state_sessions("all", None))
    assert results == [("ks", "2020"), ("wy", "2020")]


def test_yield_state_sessions_all_sessions(sessions):
    # just the latest session for each state
    results = list(yield_state_sessions("all_sessions", None))
    assert results == [
        ("ks", "2019"),
        ("ks", "2020"),
        ("wy", "2017"),
        ("wy", "2018"),
        ("ak", "2017"),
        ("ak", "2018"),
        ("ne", "2017"),
        ("ne", "2018"),
    ]
