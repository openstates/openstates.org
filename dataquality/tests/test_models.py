from django.test import TestCase
from django.utils import timezone
from opencivicdata.core.models import Jurisdiction, Division
from pupa.models import RunPlan
from dataquality.models import DataQualityIssue
from dataquality.issues import IssueType


class DataQualityIssueModelTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=True,
                               start_time=start_time, end_time=end_time)

    def test_dataqualityissue_issue_choices(self):
        """
        Issue choices must be updated on the DB migrations
        """
        self.assertEqual(DataQualityIssue._meta.get_field('issue').choices,
                         IssueType.choices())
