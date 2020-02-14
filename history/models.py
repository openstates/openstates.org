from django.db import models
from django.contrib.postgres.fields import JSONField


class Change(models.Model):
    event_time = models.DateTimeField(editable=False)
    table_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=45)
    old = JSONField(null=True)
    new = JSONField(null=True)

    @property
    def change_type(self):
        if self.old is None:
            return "create"
        elif self.new is None:
            return "delete"
        else:
            return "update"

    class Meta:
        ordering = ["event_time"]
