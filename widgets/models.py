import uuid
from django.db import models


class WidgetType(models.TextChoices):
    STATE_LEGISLATORS = "SL", "State Legislators"


class WidgetConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    widget_type = models.CharField(
        max_length=3, choices=WidgetType.choices, default=WidgetType.STATE_LEGISLATORS
    )
    settings = models.JSONField()
