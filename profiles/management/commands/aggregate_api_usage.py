import re
import json
from collections import defaultdict, Counter
from django.core.management.base import BaseCommand
from rrl import RateLimiter
from ...models import UsageReport, Profile

v1_endpoint_mapping = [
    ("^/api/v1/legislators/geo/$", "v1.geo"),
    ("^/api/v1/legislators/$", "v1.legislator-list"),
    (r"^/api/v1/legislators/\w{3}\d{6}", "v1.legislator-detail"),
    ("^/api/v1/metadata/$", "v1.metadata-list"),
    (r"^/api/v1/metadata/\w{2}/$", "v1.metadata-detail"),
    ("^/api/v1/bills/$", "v1.bills-list"),
    (r"^/api/v1/bills/\w\w.+", "v1.bills-detail"),
    ("^/api/v1/events/$", "v1.events"),
    ("^/api/v1/districts/", "v1.districts"),
    ("^/api/v1/committees/", "v1.committees"),
]


class Command(BaseCommand):
    help = "aggregate usage reports for API keys"

    def add_arguments(self, parser):
        parser.add_argument("filenames", nargs="+")

    def process_log_line(self, line):
        day = line["timestamp"][:10]
        if line["event"] == "graphql":
            endpoint = "graphql"
        elif line["event"] == "v1":
            for regex, endpoint in v1_endpoint_mapping:
                if re.match(regex, line["url"]):
                    break
            else:
                print("unknown v1 endpoint: " + line["url"])
                return
        self.count_by_day[day][(line["api_key"], endpoint)] += 1
        self.duration_by_day[day][line["api_key"]][endpoint] += line["duration"]
        self.lines += 1

    def process_file(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                if line.startswith("{"):
                    self.process_log_line(json.loads(line))

    def handle(self, *args, **options):
        # day -> (key, endpoint) -> #
        self.count_by_day = defaultdict(Counter)
        self.duration_by_day = defaultdict(
            lambda: defaultdict(lambda: defaultdict(float))
        )
        self.lines = 0

        for filename in options["filenames"]:
            self.process_file(filename)

        print(f"processed {self.lines} lines")

        # don't use the oldest day, it is probably a partial and will overwrite good data
        newest_day = "2000-01-01"
        oldest_day = "2100-01-01"
        for day in self.count_by_day.keys():
            if day > newest_day:
                newest_day = day
            if day < oldest_day:
                oldest_day = day
        print(f"found logs from {oldest_day} to {newest_day}, dropping {oldest_day}")

        keys = {key.api_key: key for key in Profile.objects.all()}

        limiter = RateLimiter(
            prefix="v3", tiers=[], use_redis_time=False, track_daily_usage=True
        )

        for key in keys:
            usage = limiter.get_usage_since(key, oldest_day)
            for daily_usage in usage:
                UsageReport.objects.update_or_create(
                    profile=keys[key],
                    date=daily_usage.day,
                    endpoint="v3",
                    defaults=dict(calls=daily_usage.calls, total_duration_seconds=0),
                )

        for day, counter in self.count_by_day.items():
            # skip oldest day
            if day == oldest_day:
                continue

            # build log-based usage reports
            for (key, endpoint), calls in counter.items():
                duration = self.duration_by_day[day][key][endpoint]

                # convert key
                try:
                    profile = keys[key]
                except KeyError:
                    print(f"unknown key {key} with {calls} calls")
                    continue

                UsageReport.objects.update_or_create(
                    profile=profile,
                    date=day,
                    endpoint=endpoint,
                    defaults=dict(calls=calls, total_duration_seconds=duration),
                )
