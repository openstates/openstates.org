import datetime
import pytest
from freezegun import freeze_time
from django.contrib.auth.models import User
from ..models import KEY_TIERS, Limit
from ..verifier import (
    CacheBackend,
    verify,
    VerificationError,
    RateLimitError,
    QuotaError,
)


KEY_TIERS.update(
    {
        "inactive": {"name": "Not Yet Activated"},
        "suspended": {"name": "Suspended"},
        "bronze": {"name": "bronze", "default": Limit(100, 2, 10)},
        "silver": {
            "name": "silver",
            "default": Limit(10, 1, 10),
            "premium": Limit(10, 1, 10),
        },
        "gold": {
            "name": "Gold",
            "default": Limit(100, 2, 10),
            "premium": Limit(10, 1, 2),
        },
    }
)


def _create_key(key, tier):
    u = User.objects.create(username=key)
    u.profile.api_key = key
    u.profile.api_tier = tier
    u.profile.save()


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


@pytest.mark.django_db
def test_verifier_bad_key():
    pytest.raises(VerificationError, verify, "badkey", "bronze")


@pytest.mark.django_db
def test_verifier_inactive_key():
    _create_key("newkey", "inactive")
    pytest.raises(VerificationError, verify, "newkey", "bronze")


@pytest.mark.django_db
def test_verifier_suspended_key():
    _create_key("newkey", "suspended")
    pytest.raises(VerificationError, verify, "newkey", "bronze")


@pytest.mark.django_db
def test_verifier_zone_access():
    _create_key("goldkey", "gold")
    _create_key("bronzekey", "bronze")

    # bronze can get default
    assert verify("bronzekey", "default") is True
    # gold has access, bronze doesn't
    assert verify("goldkey", "premium") is True
    pytest.raises(VerificationError, verify, "bronzekey", "premium")


@pytest.mark.django_db
def test_verifier_rate_limit():
    _create_key("vrl", "bronze")

    with freeze_time() as frozen_dt:
        # to start - we should have full capacity for a burst of 10
        for x in range(10):
            verify("vrl", "default")

        # this next one should raise an exception
        pytest.raises(RateLimitError, verify, "vrl", "default")

        # let's go forward 1sec, this will let the bucket get 2 more tokens
        frozen_dt.tick()

        # two more, then limited
        verify("vrl", "default")
        verify("vrl", "default")
        pytest.raises(RateLimitError, verify, "vrl", "default")


@pytest.mark.django_db
def test_verifier_rate_limit_full_refill():
    _create_key("vrlfr", "gold")

    with freeze_time() as frozen_dt:
        # let's use the premium zone now - 1req/sec. & burst of 2
        verify("vrlfr", "premium")
        verify("vrlfr", "premium")
        pytest.raises(RateLimitError, verify, "vrlfr", "premium")

        # in 5 seconds - ensure we haven't let capacity surpass burst rate
        frozen_dt.tick(delta=datetime.timedelta(seconds=5))
        verify("vrlfr", "premium")
        verify("vrlfr", "premium")
        pytest.raises(RateLimitError, verify, "vrlfr", "premium")


@pytest.mark.django_db
def test_verifier_rate_limit_key_dependent():
    # ensure that the rate limit is unique per-key
    _create_key("b1", "gold")
    _create_key("b2", "gold")

    # each key is able to get both of its requests in, no waiting
    verify("b1", "premium")
    verify("b1", "premium")
    verify("b2", "premium")
    verify("b2", "premium")

    pytest.raises(RateLimitError, verify, "b1", "premium")
    pytest.raises(RateLimitError, verify, "b2", "premium")


@pytest.mark.django_db
def test_verifier_rate_limit_zone_dependent():
    # ensure that the rate limit is unique per-zone
    _create_key("zonedep", "gold")

    # key is able to get both of its requests in, no waiting
    verify("zonedep", "premium")
    verify("zonedep", "premium")
    # and can hit another zone no problem
    verify("zonedep", "default")

    # but premium is still exhausted
    pytest.raises(RateLimitError, verify, "zonedep", "premium")


@pytest.mark.django_db
def test_verifier_quota_day():
    _create_key("vqd", "silver")

    with freeze_time("2017-04-17") as frozen_dt:
        # silver can hit premium only 10x/day (burst is also 10)
        for x in range(10):
            verify("vqd", "premium")

        # after 1 second, should have another token
        frozen_dt.tick()

        # but still no good- we've hit our daily limit
        pytest.raises(QuotaError, verify, "vqd", "premium")

        # let's pretend a day has passed, we can call again!
        frozen_dt.tick(delta=datetime.timedelta(days=1))
        for x in range(10):
            verify("vqd", "premium")


@pytest.mark.django_db
def test_verifier_quota_key_dependent():
    _create_key("vqk1", "gold")
    _create_key("vqk2", "gold")

    with freeze_time("2017-04-17") as frozen_dt:
        # 1 req/sec from vqk1 and vqk1
        for x in range(10):
            verify("vqk1", "premium")
            verify("vqk2", "premium")
            frozen_dt.tick()

        # 11th in either should be a problem - day total is exhausted
        pytest.raises(QuotaError, verify, "vqk1", "premium")
        pytest.raises(QuotaError, verify, "vqk2", "premium")


@pytest.mark.django_db
def test_verifier_quota_zone_dependent():
    _create_key("qzd", "silver")

    with freeze_time("2017-04-17") as frozen_dt:
        # should be able to do 10 in premium & secret without issue
        for x in range(10):
            verify("qzd", "premium")
            verify("qzd", "default")
            frozen_dt.tick()

        # 11th in either should be a problem
        pytest.raises(QuotaError, verify, "qzd", "premium")
        pytest.raises(QuotaError, verify, "qzd", "default")
