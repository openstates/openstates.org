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
        self.person.contact_details.create(type='voice', value='9999999999')
        self.person.contact_details.create(type='email', value='email@openstates.com')
        self.person.contact_details.create(type='address', value='USA')


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
        
        # Covers the possibility of creating more than one object with data
        pre_issue_count = DataQualityIssue.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': "invalid_object",
            'issue': 'wrong-email'
        }
        response = self.client.post(reverse('report'), data)

        post_issue_count = DataQualityIssue.objects.all().count()
        exception_raised = False
        try:
            DataQualityIssue.objects.get(object_id="invalid_object")
        except:
            exception_raised = True

        self.assertEqual(pre_issue_count, post_issue_count)
        self.assertTrue(exception_raised)

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
        exception_raised = False
        try:
            DataQualityIssue.objects.get(jurisdiction__id = "invalid_object")
        except:
            exception_raised = True

        self.assertEqual(pre_issue_count, post_issue_count)
        self.assertTrue(exception_raised)

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
        exception_raised = False
        try:
            DataQualityIssue.objects.get(issue = "invalid-issue")
        except:
            exception_raised = True

        self.assertEqual(pre_issue_count, post_issue_count)
        self.assertTrue(exception_raised)

    # same data should not be added twice
    def test_view_issue_already_exist(self):
        
        pre_issue_count = DataQualityIssue.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'issue': 'wrong-phone'
        }
        response = self.client.post(reverse('report'), data)

        post_issue_count = DataQualityIssue.objects.all().count()
        issue = DataQualityIssue.objects.get(issue="wrong-phone",
                                             object_id=self.person.id)
        
        self.assertEqual(pre_issue_count+1, post_issue_count)
        pre_issue_count = post_issue_count

        response = self.client.post(reverse('report'), data)
        count = DataQualityIssue.objects.filter(issue="wrong-phone",
                                                object_id=self.person.id).count()

        post_issue_count = DataQualityIssue.objects.all().count()
        self.assertEqual(pre_issue_count, post_issue_count)
        self.assertEqual(count, 1)


class ResolveTests(BaseViewTestCase):
    
    def test_view_response(self):
        response = self.client.get(reverse('resolve'))
        self.assertEqual(response.status_code, 200)

    # valid Resolver should be added
    def test_view_valid_resolve(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'newemail@openstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99@gmail.com'
        }
        response = self.client.post(reverse('resolve'), data)

        post_resolve_count = IssueResolverPatch.objects.all().count()
        resolve = IssueResolverPatch.objects.get(jurisdiction = self.jur.id, 
                                                object_id=self.person.id,
                                                old_value='email@openstates.com',
                                                new_value='newemail@openstates.com',
                                                category='email',
                                                note='correcting email',
                                                source='http://google.com',
                                                reporter_name='bikram',
                                                reporter_email='bikram.bharti99@gmail.com')

        self.assertEqual(pre_resolve_count+1, post_resolve_count)

    # Invalid jurisdiction for resolver
    def test_view_invalid_jurisdiction(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': "invalidJurId",
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'email2@openstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99@gmail.comm' # Note here, Email is changed
        }
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(jurisdiction__id="invalidJurId")
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # Invalid reporter_email for resolver
    def test_view_invalid_email(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'newemail@openstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikrambharti'
        }
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(reporter_email="bikram.bharti99gmail.com")
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)
        
    # Invalid Url in source for resolver
    def test_view_invalid_url(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'email2@lopenstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'google',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99gmail.comm'
        }
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(source="google")
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # Invalid category for resolver
    def test_view_invalid_category(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'email2@openstates.com',
            'category': 'invalid_category',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99gmail.comm'
        }
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(category="invalid_category")
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # Invalid object_id for resolver
    def test_view_invalid_object_id(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': "invalid_id",
            'old_value': 'email@openstates.com',
            'new_value': 'email2@openstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99gmail.comm'
        }
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(object_id="invalid_id")
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # Vacant data submission test
    def test_view_vacant_data(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {}
        response = self.client.post(reverse('resolve'), data)

        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)

    # Invalid old_value, for a particular object for resolver
    def test_view_invalid_old_value(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': '123456789',
            'new_value': '123456781',
            'category': 'phone',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99@gmail.com'
        }
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(old_value="123456789",
                                           object_id=self.person.id)
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # Category and old_value don't correspond
    def test_view_category_old_value_not_matching(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'email2@openstates.com',
            'category': 'phone',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99@gmail.comm'
        }
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(category="phone",
                                           old_value="email@openstates.com")
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # (valid)object_id and old_value don't correspond
    def test_view_old_value_object_id_not_matching(self):
        new_person = Person.objects.create(name="james")
        new_person.contact_details.create(type="email", value="j@open.com")
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': new_person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'email2@openstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99@gmail.com'
        }
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(old_value="email@openstates.com",
                                           object_id=new_person.id)           
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # User with an email only allowed to add patch for a particular category
    # in a particular object with unreviewed status
    def test_view_repeated_patch_with_same_reporter_email(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'email2@openstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99@gmail.com'
        }
        
        response = self.client.post(reverse('resolve'), data)
        post_resolve_count = IssueResolverPatch.objects.all().count()

        self.assertEqual(pre_resolve_count+1, post_resolve_count)
        pre_resolve_count = post_resolve_count

        # same reporter_email,same object_id, same category
        # different new_value
        data['new_value'] = 'bikram99@gmail.com'
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(new_value="email@openstates.com",
                                           object_id=self.person.id,
                                           reporter_email='bikram.bharti99@gmail.com')           
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # Patch with same new_value can't be added for a particular category
    # in a particular object with unreviewed status
    def test_view_same_new_value_same_category(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'newemail@openstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99@gmail.commm'
        }
        response = self.client.post(reverse('resolve'), data)
        post_resolve_count = IssueResolverPatch.objects.all().count()

        self.assertEqual(pre_resolve_count+1, post_resolve_count)
        pre_resolve_count = post_resolve_count

        # same new value, but with different report_email
        data['reporter_email'] = 'bikram99@gmail.com'
        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            IssueResolverPatch.objects.get(new_value="newemail@openstates.com",
                                           object_id=self.person.id,
                                           reporter_email='bikram99@gmail.com')           
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count, post_resolve_count)
        self.assertTrue(excpetion_raised)

    # Patch with same new_value can be added for a particular category
    # in a particular object with status other than unreviewed
    def test_view_same_new_value_same_category_change_status(self):
        pre_resolve_count = IssueResolverPatch.objects.all().count()
        data = {
            'jurisdiction': self.jur.id,
            'object_id': self.person.id,
            'old_value': 'email@openstates.com',
            'new_value': 'newemail@openstates.com',
            'category': 'email',
            'note': 'correcting email',
            'source': 'http://google.com',
            'reporter_name': 'bikram',
            'reporter_email': 'bikram.bharti99@gmail.commm'
        }
        response = self.client.post(reverse('resolve'), data)
        post_resolve_count = IssueResolverPatch.objects.all().count()

        self.assertEqual(pre_resolve_count+1, post_resolve_count)
        pre_resolve_count = post_resolve_count

        # same new value, but with different report_email
        data['reporter_email'] = 'bikram99@gmail.com'

        # Change status to approved
        resolve = IssueResolverPatch.objects.get(category='email',
                                                 object_id=self.person.id,
                                                 new_value="newemail@openstates.com")
        resolve.status = 'approved'
        resolve.save()

        response = self.client.post(reverse('resolve'), data)

        excpetion_raised = False
        try:
            resolve = IssueResolverPatch.objects.get(new_value="newemail@openstates.com",
                                           object_id=self.person.id,
                                           reporter_email='bikram99@gmail.com')           
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count+1, post_resolve_count)
        self.assertFalse(excpetion_raised)
        
        pre_resolve_count = post_resolve_count

        resolve.status = 'rejected'
        resolve.save()

        # same reporter email, different new_value
        data['new_value'] = 'email23@open.com'
        response = self.client.post(reverse('resolve'), data)
        try:
            resolve = IssueResolverPatch.objects.get(new_value="email23@open.com",
                                                     object_id=self.person.id,
                                                     reporter_email='bikram99@gmail.com')           
        except:
            excpetion_raised = True
        
        post_resolve_count = IssueResolverPatch.objects.all().count()
        self.assertEqual(pre_resolve_count+1, post_resolve_count)
        self.assertFalse(excpetion_raised)


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


    