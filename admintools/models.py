from admintools import issues
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class DataQualityIssue(models.Model):
    content_type = models.ForeignKey(ContentType,
                                     related_name="dataquality_issues")
    object_id = models.CharField(max_length=300)
    content_object = GenericForeignKey('content_type', 'object_id')

    alert = models.CharField(max_length=50, choices=issues.IssueType.choices())
    issue = models.CharField(max_length=100)
    reporter = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'opencivicdata_dataqualityissue'
        index_together = [
            ['alert', 'issue']
        ]

    def __str__(self):
        return '{} issue type - {}'.format(self.get_issue_display(),
                                           self.get_alert_display())
