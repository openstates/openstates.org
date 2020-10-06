import uuid
from django.db import models
from django.contrib.auth.models import User


class WidgetType(models.TextChoices):
    STATE_LEGISLATORS = "SL", "State Legislators"


class WidgetConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, related_name="widgets", on_delete=models.CASCADE)
    name = models.TextField(max_length=50)
    widget_type = models.CharField(
        max_length=3, choices=WidgetType.choices, default=WidgetType.STATE_LEGISLATORS,
    )
    settings = models.JSONField(blank=True, default=dict)

    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.id}"

    def url(self):
        return f"/w/{self.id}"
