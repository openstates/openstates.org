from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    organization_name = models.CharField(max_length=100, blank=True)
    about = models.TextField(blank=True)

    # feature flags
    feature_subscriptions = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.user}"
