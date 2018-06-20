from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from opencivicdata.core.models import Jurisdiction

from . import issues


class CrowdSourceIssue(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('ignored', 'Ignored')
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.CharField(max_length=300)
    content_object = GenericForeignKey('content_type', 'object_id')

    jurisdiction = models.ForeignKey(Jurisdiction, related_name="crowdsource_issues",
                                     on_delete=models.CASCADE)
    issue = models.CharField(max_length=150, choices=issues.IssueType.choices())
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    message = models.TextField(blank=True)

    reporter_email = models.EmailField(blank=True)
    reporter_name = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return '{} issue type'.format(self.issue)
