from django.db import models
from opencivicdata.legislative.models import LegislativeSession


class DataExport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(LegislativeSession, on_delete=models.CASCADE)
    url = models.URLField()
    notes = models.TextField(blank=True)
