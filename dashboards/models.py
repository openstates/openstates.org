from django.db import models
from openstates.data.models import LegislativeSession


class DataQualityReport(models.Model):

    chamber = models.CharField(max_length=20)
    session = models.ForeignKey(LegislativeSession, on_delete=models.CASCADE)

    total_bills = models.PositiveIntegerField()
    latest_bill_created_date = models.DateTimeField(null=True)
    latest_action_date = models.DateTimeField(null=True)
    earliest_action_date = models.DateTimeField(null=True)

    average_sponsors_per_bill = models.PositiveIntegerField()
    min_sponsors_per_bill = models.PositiveIntegerField()
    max_sponsors_per_bill = models.PositiveIntegerField()

    average_actions_per_bill = models.PositiveIntegerField()
    min_actions_per_bill = models.PositiveIntegerField()
    max_actions_per_bill = models.PositiveIntegerField()

    average_votes_per_bill = models.PositiveIntegerField()
    min_votes_per_bill = models.PositiveIntegerField()
    max_votes_per_bill = models.PositiveIntegerField()

    average_documents_per_bill = models.PositiveIntegerField()
    min_documents_per_bill = models.PositiveIntegerField()
    max_documents_per_bill = models.PositiveIntegerField()

    average_versions_per_bill = models.PositiveIntegerField()
    min_versions_per_bill = models.PositiveIntegerField()
    max_versions_per_bill = models.PositiveIntegerField()

    total_bills_no_sources = models.PositiveIntegerField()
    total_votes_no_sources = models.PositiveIntegerField()

    number_of_subjects_in_chamber = models.PositiveIntegerField()
    number_of_bills_without_subjects = models.PositiveIntegerField()

    total_bills_without_versions = models.PositiveIntegerField()

    total_votes_without_voters = models.PositiveIntegerField()
    total_votes_bad_counts = models.PositiveIntegerField()
