import time
import datetime
from django.core.cache import caches
from django.http import JsonResponse
from .models import Profile


class VerificationError(Exception):
    pass


class RateLimitError(Exception):
    pass


class QuotaError(Exception):
    pass


class CacheBackend:
    def __init__(self):
        self.cache = caches["default"]
        # keep entries in cache for 48 hours
        self.timeout = 48 * 60 * 60

    def get_tokens_and_timestamp(self, key, zone):
        kz = "{}~{}".format(key, zone)
        return self.cache.get_or_set(kz, lambda: (0, None), self.timeout)

    def set_token_count(self, key, zone, tokens):
        kz = "{}~{}".format(key, zone)
        self.cache.set(kz, (tokens, time.time()), self.timeout)

    def get_and_inc_quota_value(self, key, zone, quota_range):
        quota_key = "{}~{}~{}".format(key, zone, quota_range)
        self.cache.get_or_set(quota_key, lambda: 0, timeout=self.timeout)
        # sometimes calling get_or_set followed by incr leads to an error where the
        # get or set hasn't landed yet, so we'll special case the creation case
        try:
            return self.cache.incr(quota_key)
        except ValueError:
            return 1


backend = CacheBackend()


def verify(key, zone):
    if not key:
        raise VerificationError("must provide an API key")
    # ensure we have a verified key w/ access to the zone
    try:
        # could also do this w/ new subquery expressions in 1.11
        profile = Profile.objects.get(api_key=key)
        limit = profile.get_tier_details().get(zone)
    except Profile.DoesNotExist:
        raise VerificationError("no valid key")
    if not limit:
        raise VerificationError("key does not have access to zone {}".format(zone))

    # enforce rate limiting - will raise RateLimitError if exhausted
    # replenish first
    tokens, last_time = backend.get_tokens_and_timestamp(key, zone)

    if last_time is None:
        # if this is the first time, fill the bucket
        tokens = limit.burst_size
    else:
        # increment bucket, careful not to overfill
        tokens = min(
            tokens + (limit.requests_per_second * (time.time() - last_time)),
            limit.burst_size,
        )

    # now try to decrement count
    if tokens >= 1:
        tokens -= 1
        backend.set_token_count(key, zone, tokens)
    else:
        raise RateLimitError(
            "exhausted tokens: {} req/sec, burst {}".format(
                limit.requests_per_second, limit.burst_size
            )
        )

    # enforce daily quota
    quota_range = datetime.datetime.utcnow().strftime("%Y%m%d")

    if backend.get_and_inc_quota_value(key, zone, quota_range) > limit.daily_requests:
        raise QuotaError(f"quota exceeded: {limit.daily_requests}/day")

    return True


def get_key_from_request(request):
    key = request.META.get("HTTP_X_API_KEY")
    if not key:
        key = request.GET.get("apikey")
    return key


def verify_request(request, zone):
    if zone == "v1":
        ERROR_NOTE = (
            "Please consider moving to API v2 or v3.  API v1 will be removed in Summer 2021. "
            "If you are seeing this message please email contact@openstates.org and "
            "your v1 grace period can be extended."
        )
    else:
        ERROR_NOTE = (
            "Login and visit https://openstates.org/account/profile/ for your API key. "
            "contact@openstates.org to raise limits"
        )

    key = get_key_from_request(request)

    try:
        verify(key, zone)
    except VerificationError as e:
        return JsonResponse({"error": str(e), "note": ERROR_NOTE}, status=403)
    except RateLimitError as e:
        return JsonResponse({"error": str(e), "note": ERROR_NOTE}, status=429)
    except QuotaError as e:
        return JsonResponse({"error": str(e), "note": ERROR_NOTE}, status=429)

    # pass through
    return None
