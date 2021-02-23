import uuid
import urllib.parse
import base62
from collections import namedtuple
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from utils.common import pretty_url
from openstates.data.models import Person, Bill
from .utils import utcnow


DAILY = "d"
WEEKLY = "w"


Limit = namedtuple("Limit", "daily_requests requests_per_second burst_size")
KEY_TIERS = {
    "inactive": {"name": "Not Yet Activated"},
    "suspended": {"name": "Suspended"},
    "default": {
        "name": "Default (new user)",
        "v1": Limit(0, 1, 2),
        "v2": Limit(500, 1, 2),
    },
    "legacy": {"name": "Legacy", "v1": Limit(1000, 1, 2), "v2": Limit(3000, 2, 3)},
    "bronze": {"name": "Bronze", "v1": Limit(0, 1, 1), "v2": Limit(3000, 2, 3)},
    "silver": {"name": "Silver", "v1": Limit(1000, 1, 2), "v2": Limit(30000, 2, 5)},
    "unlimited": {
        "name": "Unlimited",
        "v1": Limit(1000000, 100000, 100000),
        "v2": Limit(1000000, 100000, 100000),
    },
}
KEY_TIER_CHOICES = [(k, v["name"]) for k, v in KEY_TIERS.items()]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    organization_name = models.CharField(max_length=100, blank=True)
    about = models.TextField(blank=True)

    # feature flags
    feature_subscriptions = models.BooleanField(default=True)

    # subscriptions
    subscription_emails_html = models.BooleanField(default=True)
    subscription_frequency = models.CharField(
        max_length=1, choices=((DAILY, "daily"), (WEEKLY, "weekly")), default=WEEKLY
    )
    subscription_last_checked = models.DateTimeField(default=utcnow)

    # API key
    api_key = models.CharField(max_length=40, default=uuid.uuid4)
    api_tier = models.SlugField(
        max_length=50, choices=KEY_TIER_CHOICES, default="inactive"
    )

    def get_tier_details(self):
        if self.api_tier not in KEY_TIERS:
            # don't actually write to db on this call
            self.api_tier = "inactive"
        return KEY_TIERS[self.api_tier]

    def __str__(self):
        return f"Profile for {self.user}"

    class Meta:
        indexes = [
            models.Index(fields=["api_key"]),
        ]


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    query = models.CharField(max_length=300, blank=True)
    state = models.CharField(max_length=2, blank=True)
    chamber = models.CharField(max_length=15, blank=True)
    session = models.CharField(max_length=100, blank=True)
    classification = models.CharField(max_length=50, blank=True)
    subjects = ArrayField(models.CharField(max_length=100), blank=True)
    status = ArrayField(models.CharField(max_length=50), blank=True)
    sponsor = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,
        blank=True,
    )
    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,
        blank=True,
    )

    @property
    def subscription_type(self):
        if self.bill_id:
            return "bill"
        elif self.query:
            return "query"
        elif self.sponsor_id:
            return "sponsor"
        raise ValueError(f"invalid subscription: {self.__dict__}")

    @property
    def pretty(self):
        if self.subscription_type == "bill":
            return f"Updates on {self.bill}"
        elif self.subscription_type == "sponsor":
            return f"Bills sponsored by {self.sponsor}"
        elif self.subscription_type == "query":
            state = self.state.upper() if self.state else "all states"
            pretty_str = f"Bills matching '{self.query}' from {state}"
            if self.chamber in ("upper", "lower"):
                pretty_str += f", {self.chamber} chamber"
            if self.session:
                pretty_str += f", {self.session}"
            if self.classification:
                pretty_str += f", classified as {self.classification}"
            if self.subjects:
                pretty_str += f", including subjects '{', '.join(self.subjects)}'"
            if self.status:
                pretty_str += f", status includes '{', '.join(self.status)}'"
            if self.sponsor:
                pretty_str += f", sponsored by {self.sponsor}"
            return pretty_str

    @property
    def site_url(self):
        if self.subscription_type == "query":
            queryobj = {
                "query": self.query,
                "subjects": self.subjects or [],
                "status": self.status or [],
            }
            if self.classification:
                queryobj["classification"] = self.classification
            if self.session:
                queryobj["session"] = self.session
            if self.chamber:
                queryobj["chamber"] = self.chamber
            if self.sponsor_id:
                queryobj["sponsor_id"] = self.sponsor_id
            querystr = urllib.parse.urlencode(queryobj, doseq=True)
            if self.state:
                return f"/{self.state}/bills/?{querystr}"
            else:
                return f"/search/?{querystr}"
        elif self.subscription_type == "bill":
            return pretty_url(self.bill)
        elif self.subscription_type == "sponsor":
            return pretty_url(self.sponsor)

    def __str__(self):
        return f"{self.user}: {self.pretty}"


def _str_uuid():
    return base62.encode(uuid.uuid4().int)


class Notification(models.Model):
    id = models.CharField(
        primary_key=True, default=_str_uuid, max_length=22, editable=False
    )
    # store email instead of link to user, since emails can change and users can be deleted
    email = models.EmailField(editable=False)
    sent = models.DateTimeField(editable=False)
    num_query_updates = models.PositiveIntegerField(editable=False)
    num_bill_updates = models.PositiveIntegerField(editable=False)


class UsageReport(models.Model):
    profile = models.ForeignKey(
        Profile,
        related_name="usage_reports",
        on_delete=models.CASCADE,
        default=None,
        null=True,
    )
    date = models.DateField()
    endpoint = models.CharField(max_length=100)
    calls = models.PositiveIntegerField()
    total_duration_seconds = models.PositiveIntegerField()

    class Meta:
        unique_together = ("profile", "date", "endpoint")
