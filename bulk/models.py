from django.db import models
from openstates.data.models import LegislativeSession


class DataExport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session = models.ForeignKey(LegislativeSession, on_delete=models.CASCADE)
    data_type = models.CharField(
        max_length=4, choices=(("csv", "csv"), ("json", "json"))
    )
    url = models.URLField()
    notes = models.TextField(blank=True)
