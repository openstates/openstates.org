from django.test import TestCase
from django.urls import reverse
from django.template import Template, Context

from opencivicdata.core.models import Jurisdiction, Person, Division
from dataquality.models import DataQualityIssue, IssueResolverPatch


class BaseViewTestCase(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        self.jur = Jurisdiction.objects.create(
            id="ocd-division/country:us/state:mo",
            name="Missouri State Senate",
            url="http://www.senate.mo.gov",
            division=division,
        )
        self.person = Person.objects.create(name='Bikram Bharti')

class ReportTests(BaseViewTestCase):
    
    def test_view_response(self):
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)

class ResolveTests(BaseViewTestCase):
    
    def test_view_response(self):
        response = self.client(reverse('resolve'))
        self.assertEqual(response.status_code, 200)

class ListTests(BaseViewTestCase):

    def test_view_response(self):
        response = self.client(reverse('list'))
        self.assertEqual(response.status_code, 200)
    
    def test_issue_count(self):
        response = self.client(reverse('list'))
        assertEqual(len(response.context['issues']), 0)
        issue = DataQualityIssue.objects.create(content_object=self.person,
                                                Jurisdiction=self.jur,
                                                issue='wrong-email')
        assertEqual(len(response.context['issues']), 1)
        issue = DataQualityIssue.objects.create(content_object=self.person,
                                                Jurisdiction=self.jur,
                                                issue='wrong-phone')
        assertEqual(len(response.context['issues']), 2)


    