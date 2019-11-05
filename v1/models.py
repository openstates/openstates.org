from django.contrib.gis.db import models
from opencivicdata.legislative.models import Bill


class LegacyBillMapping(models.Model):
    legacy_id = models.CharField(max_length=20, primary_key=True)
    bill = models.ForeignKey(
        Bill, related_name="legacy_mapping", on_delete=models.CASCADE
    )
