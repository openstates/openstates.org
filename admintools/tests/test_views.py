from django.test import TestCase
from pupa.models import RunPlan
from opencivicdata.core.models import Jurisdiction, Person, Division
from django.utils import timezone
from admintools.models import DataQualityIssue
from django.core.urlresolvers import reverse


class OverviewViewTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur1 = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        jur2 = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:da",
                name="Dausa State Senate",
                url="http://www.senate.da.gov",
                division=division,
            )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur1, success=True,
                               start_time=start_time, end_time=end_time)
        start_time = end_time + timezone.timedelta(minutes=10)
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur2, success=True,
                               start_time=start_time, end_time=end_time)

    def test_run_status_count(self):
        """
        count = None (if only last run failed)
        count = 0 (if last run was successful)
        count = X (last X runs failed, where X > 1)
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=False,
                               start_time=start_time, end_time=end_time)

        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        for item in response.context['rows']:
            if item[0] == jur.name:
                run_count = item[1]['run'].get('count')
        self.assertEqual(run_count, None)

        start_time = end_time + timezone.timedelta(minutes=10)
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=True,
                               start_time=start_time, end_time=end_time)
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        for item in response.context['rows']:
            if item[0] == jur.name:
                run_count = item[1]['run'].get('count')
        self.assertEqual(run_count, 0)

        start_time = end_time + timezone.timedelta(minutes=10)
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=False,
                               start_time=start_time, end_time=end_time)
        start_time = end_time + timezone.timedelta(minutes=10)
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=False,
                               start_time=start_time, end_time=end_time)

        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        for item in response.context['rows']:
            if item[0] == jur.name:
                run_count = item[1]['run'].get('count')
        self.assertEqual(run_count, 2)

    def test_total_rows_count_no_dataqissue(self):
        """
        Total number of rows must be equal to total number of
        jurisdictions when there are no Data Quality Issues present.
        """
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rows']), 2)

    def test_total_rows_count_partial_dataqissue(self):
        """
        Total number of rows must be equal to total number of
        jurisdictions when some of them have Data Quality Issues.
        """
        jur1 = Jurisdiction.objects.get(name="Missouri State Senate")
        person = Person.objects.create(name="Hitesh Garg")
        DataQualityIssue.objects.create(content_object=person,
                                        issue='missing-photo',
                                        alert='warning',
                                        jurisdiction=jur1)
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rows']), 2)

        def test_total_rows_count_all_dataqissue(self):
            """
            Total number of rows must be equal to total number of
            jurisdictions when all of them have Data Quality Issues.
            """
            jur1 = Jurisdiction.objects.get(name="Missouri State Senate")
            jur2 = Jurisdiction.objects.get(name="Dausa State Senate")
            person1 = Person.objects.create(name="Hitesh Garg")
            DataQualityIssue.objects.create(content_object=person1,
                                            issue='missing-photo',
                                            alert='warning',
                                            jurisdiction=jur1)
            person2 = Person.objects.create(name="Garg Hitesh")
            DataQualityIssue.objects.create(content_object=person2,
                                            issue='missing-photo',
                                            alert='warning',
                                            jurisdiction=jur2)
            response = self.client.get(reverse('overview'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['rows']), 2)

    def test_overview_with_jurisdictions(self):
        """
        Check to make sure that the overview page has jurisdiction name
        displayed.
        """
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Missouri State Senate")


class JurisdictionintroViewTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur1 = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur1, success=True,
                               start_time=start_time, end_time=end_time)

        person1 = Person.objects.create(name="Hitesh Garg")
        DataQualityIssue.objects.create(content_object=person1,
                                        issue='person-missing-photo',
                                        alert='warning',
                                        jurisdiction=jur1)

    def test_dataqualityissue_count(self):
        """
        If a particular issue exists for a `related_class` then it's count
        will be greater than zero otherwise count will be zero.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.name,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['cards']['person']['missing-photo']['count'], 1)
        # some other checks
        self.assertEqual(
            response.context['cards']
            .get('organization')['no-memberships']['count'], 0)
        self.assertEqual(
            response.context['cards']['bill']
            .get('unmatched-person-sponsor')['count'], 0)


class ListissueobjectsViewTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur1 = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur1, success=True,
                               start_time=start_time, end_time=end_time)

        person1 = Person.objects.create(name="Hitesh Garg")
        DataQualityIssue.objects.create(content_object=person1,
                                        issue='person-missing-photo',
                                        alert='warning',
                                        jurisdiction=jur1)

    def test_important_context_values(self):
        """
        To check that important context values are present.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        response = self.client.get(reverse('list_issue_objects',
                                           args=(jur.name,
                                                 'person',
                                                 'missing-photo')))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('objects' in response.context)
        self.assertTrue('url_slug' in response.context)
        self.assertTrue('jur_name' in response.context)
