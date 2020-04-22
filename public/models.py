from django.db import models
from openstates.data.models import Bill


class BillStatus(models.Model):
    bill = models.OneToOneField(Bill, on_delete=models.DO_NOTHING, primary_key=True)
    first_action_date = models.CharField(max_length=25)
    latest_action_date = models.CharField(max_length=25)
    latest_action_description = models.TextField()
    latest_passage_date = models.CharField(max_length=25)

    class Meta:
        managed = False
