from admintools import issues
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from opencivicdata.core.models import Jurisdiction


class DataQualityIssue(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('ignored', 'Ignored')
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=300)
    content_object = GenericForeignKey('content_type', 'object_id')
    jurisdiction = models.ForeignKey(Jurisdiction, related_name="dataquality_issues",
                                     on_delete=models.CASCADE)
    alert = models.CharField(max_length=50)
    issue = models.CharField(max_length=150,
                             choices=issues.IssueType.choices())
    reporter = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='active')
    message = models.TextField(blank=True)

    class Meta:
        index_together = [
            ['alert', 'issue']
        ]

    def __str__(self):
        return '{} issue type - {}'.format(self.issue, self.alert)


class IssueResolverPatch(models.Model):
    ALERT_CHOICES = (
        ('warning', 'Missing Value'),
        ('error', 'Wrong Value'),
    )
    CATEGORY_CHOICES = (
        ('name', 'Name'),
        ('address', 'Address'),
        ('voice', 'Phone'),
        ('email', 'Email'),
        ('image', 'Photo'),
    )
    STATUS_CHOICES = (
        ('approved', 'Approved'),
        ('unreviewed', 'Unreviewed'),
        ('deprecated', 'Deprecated'),
        ('rejected', 'Rejected')
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=300)
    content_object = GenericForeignKey('content_type', 'object_id')
    jurisdiction = models.ForeignKey(Jurisdiction,
                                     related_name="issue_resolver_patches",
                                     on_delete=models.CASCADE
                                     )
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    old_value = models.CharField(max_length=2250, blank=True)
    new_value = models.CharField(max_length=2250)
    category = models.CharField(max_length=500, choices=CATEGORY_CHOICES)
    alert = models.CharField(max_length=500, choices=ALERT_CHOICES)
    note = models.TextField(blank=True)
    source = models.URLField(max_length=2250, blank=True)
    reporter_email = models.EmailField(blank=True)
    reporter_name = models.CharField(max_length=500, blank=True)
    applied_by = models.CharField(max_length=205)  # user/admin  (choices ??)

    def __str__(self):
        return '{} patch of {} by {} ({})'.format(self.applied_by,
                                                  self.category,
                                                  self.reporter_name,
                                                  self.alert)
