from django.db import models
from django.contrib.postgres.fields import ArrayField
from .common import ALERT_CHOICES, ISSUE_CHOICES


class DataQualityIssues(models.Model):
    related_ids = ArrayField(base_field=models.CharField(max_length=300), default=list)
    alert = models.CharField(max_length=50, choices=ALERT_CHOICES)
    issue = models.CharField(max_length=50, choices=ISSUE_CHOICES)
    reporter = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'opencivicdata_dataqualityissues'
        index_together = [
            ['alert', 'issue']
        ]

    def __str__(self):
        return '{} issue type - {}'.format(self.get_issue_display(),
                                           self.get_alert_display())
