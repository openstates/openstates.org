from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
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
        if self.bill:
            return "bill"
        elif self.query:
            return "query"
        elif self.sponsor:
            return "sponsor"
        raise ValueError("invalid subscription")

    def __str__(self):
        if self.subscription_type == "bill":
            return f"{self.user} subscription to {self.bill}"
        elif self.subscription_type == "query":
            return f"{self.user} subscription to '{self.query}'"
        elif self.subscription_type == "sponsor":
            return f"{self.user} subscription to '{self.sponsor}'"
