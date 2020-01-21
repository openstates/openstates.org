import urllib.parse
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from utils.common import pretty_url
from opencivicdata.core.models import Person
from opencivicdata.legislative.models import Bill


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    organization_name = models.CharField(max_length=100, blank=True)
    about = models.TextField(blank=True)

    # feature flags
    feature_subscriptions = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.user}"


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
        raise ValueError("invalid subscription")

    @property
    def pretty(self):
        if self.subscription_type == "bill":
            return f"Updates on {self.bill}"
        elif self.subscription_type == "sponsor":
            return f"Bills sponsored by {self.sponsor}"
        elif self.subscription_type == "query":
            state = self.state.upper() if self.state else "all states"
            return f"Bills matching '{self.query}' from {state}"

    @property
    def site_url(self):
        if self.subscription_type == "query":
            queryobj = {
                "query": self.query,
                "session": self.session,
                "chamber": self.chamber,
                "classification": self.classification,
                "subjects": self.subjects or [],
                "status": self.status or [],
                "sponsor_id": self.sponsor_id or "",
            }
            querystr = urllib.parse.urlencode(queryobj, doseq=True)
            return f"/{self.state}/bills/?{querystr}"
        elif self.subscription_type == "bill":
            return pretty_url(self.bill)
        elif self.subscription_type == "sponsor":
            return pretty_url(self.sponsor)

    def __str__(self):
        return f"{self.user}: {self.pretty}"
