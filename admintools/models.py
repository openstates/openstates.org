from admintools import issues
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from opencivicdata.core.models import Jurisdiction


class DataQualityIssue(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=300)
    content_object = GenericForeignKey('content_type', 'object_id')
    jurisdiction = models.ForeignKey(Jurisdiction,
                                     related_name="dataquality_issues")
    alert = models.CharField(max_length=50)
    issue = models.CharField(max_length=150,
                             choices=issues.IssueType.choices())
    reporter = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'opencivicdata_dataqualityissue'
        index_together = [
            ['alert', 'issue']
        ]

    def __str__(self):
        return '{} issue type - {}'.format(self.issue,
                                           self.alert)


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
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=300)
    content_object = GenericForeignKey('content_type', 'object_id')
    jurisdiction = models.ForeignKey(Jurisdiction,
                                     related_name="issue_resolver_patches")
    status = models.CharField(max_length=100)
    old_value = models.CharField(max_length=2250)
    new_value = models.CharField(max_length=2250)
    category = models.CharField(max_length=500, choices=CATEGORY_CHOICES)
    alert = models.CharField(max_length=500, choices=ALERT_CHOICES)
    note = models.TextField(blank=True)
    source = models.URLField(max_length=2250)
    reporter_email = models.EmailField()
    reporter_name = models.CharField(max_length=500)
    applied_by = models.CharField(max_length=205)  # user/admin  (choices ??)

    class Meta:
        db_table = 'opencivicdata_issue_resolver_patch'

    def __str__(self):
        return '{} patch For {} by {} ({})'.format(self.applied_by,
                                                   self.category,
                                                   self.reporter_name,
                                                   self.alert)
