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

    # valid Issue should be added
    def test_view_valid_issue(self):
        pre_issue_count = DataQualityIssue.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'issue': 'wrong-email'
        }
        response = self.client.post(reverse('report'), data)

        post_issue_count = DataQualityIssue.objects.all().count()
        issue = DataQualityIssue.objects.get(jurisdiction = self.jur.id, 
                                             object_id=self.person.id,
                                             issue='wrong-email')
        self.assertEqual(pre_issue_count+1, post_issue_count)

    # issue should not be added, with invalid object_id
    def test_view_invalid_object_id(self):
        
        pre_issue_count = DataQualityIssue.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': "invalid_object",
            'issue': 'wrong-email'
        }
        response = self.client.post(reverse('report'), data)

        post_issue_count = DataQualityIssue.objects.all().count()
        issue = DataQualityIssue.objects.filter(object_id = "invalid_object")

        self.assertEqual(pre_issue_count, post_issue_count)
        self.assertEqual(issue.count(), 0)

    # issue should not be added, with invalid jurisdiction
    def test_view_invalid_object_id(self):
        
        pre_issue_count = DataQualityIssue.objects.all().count()
        data = {
            'jurisdiction': "invalid-jurisdiction",
            'object_id': self.person.id,
            'issue': 'wrong-email'
        }
        response = self.client.post(reverse('report'), data)

        post_issue_count = DataQualityIssue.objects.all().count()
        issue = DataQualityIssue.objects.filter(jurisdiction__id = "invalid-jurisdiction")

        self.assertEqual(pre_issue_count, post_issue_count)
        self.assertEqual(issue.count(), 0)

    # issue should not be added, with invalid issue
    def test_view_invalid_issue(self):

        pre_issue_count = DataQualityIssue.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'issue': 'invalid-issue'
        }
        response = self.client.post(reverse('report'), data)

        post_issue_count = DataQualityIssue.objects.all().count()
        issue = DataQualityIssue.objects.filter(issue = "invalid-issue")

        self.assertEqual(pre_issue_count, post_issue_count)
        self.assertEqual(issue.count(), 0)

    def test_view_issue_already_exist(self):
        
        pre_issue_count = DataQualityIssue.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'issue': 'wrong-phone'
        }
        response = self.client.post(reverse('report'), data)

        post_issue_count = DataQualityIssue.objects.all().count()
        issue = DataQualityIssue.objects.get(issue = "wrong-phone",
                                             object_id = self.person.id)
        
        self.assertEqual(pre_issue_count+1, post_issue_count)
        pre_issue_count = post_issue_count

        issue = DataQualityIssue.objects.get(issue = "wrong-phone",
                                             object_id = self.person.id)

        post_issue_count = DataQualityIssue.objects.all().count()
        self.assertEqual(pre_issue_count, post_issue_count)


class ResolveTests(BaseViewTestCase):
    
    def test_view_response(self):
        response = self.client.get(reverse('resolve'))
        self.assertEqual(response.status_code, 200)

class ListTests(BaseViewTestCase):

    def test_view_response(self):
        response = self.client.get(reverse('list'))
        self.assertEqual(response.status_code, 200)
    
    def test_issue_count(self):
        response = self.client.get(reverse('list'))
        self.assertEqual(len(response.context['issues']), 0)
        issue = DataQualityIssue.objects.create(content_object=self.person,
                                                jurisdiction=self.jur,
                                                issue='wrong-email')
        response = self.client.get(reverse('list'))
        self.assertEqual(len(response.context['issues']), 1)
        issue = DataQualityIssue.objects.create(content_object=self.person,
                                                jurisdiction=self.jur,
                                                issue='wrong-phone')
        response = self.client.get(reverse('list'))
        self.assertEqual(len(response.context['issues']), 2)


    