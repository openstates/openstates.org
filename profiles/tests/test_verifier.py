import pytest
from freezegun import freeze_time
from ..verifier import CacheBackend


@pytest.fixture
def cb():
    # ensure we have a fresh cache backend each time
    c = CacheBackend()
    c.cache.clear()
    return c


def test_get_tokens_and_timestamp_initial(cb):
    assert cb.get_tokens_and_timestamp("key", "zone") == (0, None)


def test_token_set_and_retrieve(cb):
    with freeze_time("2017-04-17"):
        cb.set_token_count("key", "zone", 100)
        tokens, timestamp = cb.get_tokens_and_timestamp("key", "zone")
        assert tokens == 100
        assert int(timestamp) == 1492387200  # frozen time


def test_key_and_zone_independence(cb):
    cb.set_token_count("key", "zone", 100)
    assert cb.get_tokens_and_timestamp("key2", "zone") == (0, None)
    assert cb.get_tokens_and_timestamp("key", "zone2") == (0, None)


def test_get_and_inc_quota(cb):
    assert cb.get_and_inc_quota_value("key", "zone", "20170411") == 1
    assert cb.get_and_inc_quota_value("key", "zone", "20170411") == 2
    assert cb.get_and_inc_quota_value("key", "zone", "20170412") == 1


def test_get_and_inc_quota_key_and_zone_independence(cb):
    assert cb.get_and_inc_quota_value("key", "zone", "20170411") == 1
    assert cb.get_and_inc_quota_value("key2", "zone", "20170411") == 1
    assert cb.get_and_inc_quota_value("key", "zone2", "20170411") == 1
