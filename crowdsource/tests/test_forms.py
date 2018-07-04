from django.test import TestCase
from crowdsource.issues import IssueType
from crowdsource.forms import *
from opencivicdata.core.models import Jurisdiction, Person, Division

class BaseFormTestCase(TestCase):

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

class IssueFormTestCase(BaseFormTestCase):

    # valid Form data
    def test_issueform_valid(self):
        form = IssueForm(data={'jurisdiction':self.jur.id, 
                              'object_id':self.person.id,
                              'issue': 'wrong-email',
                              'message': 'Email correction.'})

        self.assertTrue(form.is_valid(), form.errors)

    # Invalid Jurisdiction 
    def test_issueform_invalid_jurisdiction(self):
        form = IssueForm(data={'jurisdiction':"notCreatedId", 
                              'object_id':self.person.id,
                              'issue': 'wrong-email',
                              'message': 'Email correction.'})

        self.assertFalse(form.is_valid())

    # Invalid issue
    def test_issueform_invalid_issue(self):
        form = IssueForm(data={'jurisdiction':self.jur.id, 
                              'object_id':self.person.id,
                              'issue': 'random-issue',
                              'message': 'Email correction.'})

        self.assertFalse(form.is_valid())
    
    # Vacant form submission
    def test_issueform_empty_fields(self):
        form = IssueForm(data={})

        self.assertFalse(form.is_valid())
        
class ResolverFormTestCase(BaseFormTestCase):

    # valid Form data
    def test_resolverform_valid(self):
        form = ResolverForm(data = {'jurisdiction':self.jur.id,
                                    'object_id':self.person.id,
                                    'new_value':"new value",
                                    'old_value':"old value",
                                    'note':'Resolvers',
                                    'reporter_name':'bikram',
                                    'reporter_email':'bikram.bharti@gmail.com',
                                    'category': 'name',
                                    'source': 'http://google.com',
                                    })

        self.assertTrue(form.is_valid(), form.errors)
    
    # Invalid jurisdicition
    def test_resolverform_invalid_jurisdiction(self):
        form = ResolverForm(data = {'jurisdiction':"notCreatedId",
                                    'object_id':self.person.id,
                                    'new_value':"new value",
                                    'old_value':"old value",
                                    'note':'Resolvers',
                                    'reporter_name':'bikram',
                                    'reporter_email':'bikram.bharti@gmail.com',
                                    'category': 'name',
                                    'source': 'http://google.com',
                                    })

        self.assertFalse(form.is_valid())
    
    # Invalid email
    def test_resolverform_invalid_email(self):
        form = ResolverForm(data = {'jurisdiction':self.jur.id,
                                    'object_id':self.person.id,
                                    'new_value':"new value",
                                    'old_value':"old value",
                                    'note':'Resolvers',
                                    'reporter_name':'bikram',
                                    'reporter_email':'bikram.bharti',
                                    'category': 'name',
                                    'source': 'http://google.com',
                                    })

        self.assertFalse(form.is_valid())

    # Invalid url in source
    def test_resolverform_invalid_url(self):
        form = ResolverForm(data = {'jurisdiction':self.jur.id,
                                    'object_id':self.person.id,
                                    'new_value':"new value",
                                    'old_value':"old value",
                                    'note':'Resolvers',
                                    'reporter_name':'bikram',
                                    'reporter_email':'bikram.bharti@gmail.com',
                                    'category': 'name',
                                    'source': 'google',
                                    })

        self.assertFalse(form.is_valid())
    
    # Invalid category
    def test_resolverform_invalid_category(self):
        form = ResolverForm(data = {'jurisdiction':self.jur.id,
                                    'object_id':self.person.id,
                                    'new_value':"new value",
                                    'old_value':"old value",
                                    'note':'Resolvers',
                                    'reporter_name':'bikram',
                                    'reporter_email':'bikram.bharti@gmail.com',
                                    'category': 'invalidCategory',
                                    'source': 'http://google.com',
                                    })

        self.assertFalse(form.is_valid())
    
    # Vacant form submission
    def test_resolverform_empty_fields(self):
        form = ResolverForm(data = {})

        self.assertFalse(form.is_valid())
    
