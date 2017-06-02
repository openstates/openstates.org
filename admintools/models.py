from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .common import ALERT_CHOICES, ISSUE_CHOICES


class DataQualityIssues(models.Model):
    content_type = models.ForeignKey(ContentType,
                                     related_name="dataquality_issues")
    object_id = models.CharField(max_length=300)
    content_object = GenericForeignKey('content_type', 'object_id')

    alert = models.CharField(max_length=50, choices=ALERT_CHOICES)
    issue = models.CharField(max_length=50, choices=ISSUE_CHOICES)

    class Meta:
        db_table = 'opencivicdata_dataqualityissues'
        index_together = [
            ['alert', 'issue']
        ]

    def __str__(self):
        return '{} to {} - {}'.format(self.get_issue_display(),
                                      type(self.content_object).__name__,
                                      self.get_alert_display())
