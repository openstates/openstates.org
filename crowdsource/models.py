from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from opencivicdata.core.models import Jurisdiction

from . import issues
from django.contrib.auth.models import User


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

class CrowdSourceIssueResolver(models.model):
    STATUS_CHOICES = (
        ('approved', 'Approved'),
        ('unreviewed', 'Unreviewed'),
        ('deprecated', 'Deprecated'),
        ('rejected', 'Rejected')
    )

    issue = models.ForeignKey(CrowdSourceIssue, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='unreviewed')
    old_value = models.TextField(blank=True)
    new_value = models.TextField()
    note = models.TextField(blank=True)
    source = models.URLField(max_length=2250, blank=True)
    reporter_email = models.EmailField(blank=True)
    reporter_name = models.CharField(max_length=500, blank=True)
    applied_by = models.ForeignKey(User, blank=True)  # user/admin 

    def __str__(self):
        return '{} patch of {} by {}'.format(self.applied_by, self.issue, self.reporter_name)
