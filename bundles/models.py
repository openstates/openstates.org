from django.db import models
from opencivicdata.legislative.models import Bill


class Bundle(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    bills = models.ManyToManyField(Bill, through="BundleBill")


class BundleBill(models.Model):
    bundle_id = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    bill_id = models.ForeignKey(Bill, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)

    class Meta:
        unique_together = [("bundle_id", "bill_id")]
