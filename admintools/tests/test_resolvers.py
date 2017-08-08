import sys
from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from admintools.models import IssueResolverPatch, DataQualityIssue
from opencivicdata.core.models import (Person, Jurisdiction, Division,
                                       Organization, Membership,
                                       PersonContactDetail)
from admintools.resolvers.person import setup_person_resolver


class CommandsTestCase(TestCase):
    "Test `resolve issues` command"

    def test_resolve_issues_command(self):
        out = StringIO()
        sys.stout = out
        args = ['issues']
        call_command('resolve', *args, stdout=out)
        self.assertIn('Successfully Imported People Issue Resolver Patches'
                      ' into DB',
                      out.getvalue())


class PeoplePatchesTest(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        Organization.objects.create(name="Democratic", jurisdiction=jur)

    def test_name_patches(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Wrong Name")
        Membership.objects.create(person=person, organization=org)
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='deprecated',
                                          old_value='Wrong Name',
                                          new_value='Garg',
                                          category='name',
                                          alert='error',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='rejected',
                                          old_value='Wrong Name',
                                          new_value='Hitesh',
                                          category='name',
                                          alert='error',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='approved',
                                          old_value='Wrong Name',
                                          new_value='Hitesh Garg',
                                          category='name',
                                          alert='error',
                                          applied_by='admin')
        setup_person_resolver()
        # getting updated object
        p = Person.objects.get(id=person.id)
        self.assertEqual(p.name, "Hitesh Garg")

    def test_image_patches(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Wrong Image",
                                       image="http://www.image.png")
        Membership.objects.create(person=person, organization=org)
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='rejected',
                                          old_value='http://www.image.png',
                                          new_value='http://www.ht.png',
                                          category='image',
                                          alert='error',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='deprecated',
                                          old_value='http://www.image.png',
                                          new_value='http://www.rt.png',
                                          category='image',
                                          alert='error',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='approved',
                                          old_value='http://www.image.png',
                                          new_value='http://www.right.png',
                                          category='image',
                                          alert='error',
                                          applied_by='admin')
        setup_person_resolver()
        # getting updated object
        p = Person.objects.get(id=person.id)
        self.assertEqual(p.image, "http://www.right.png")

    def test_address_patches(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Wrong Address")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="New York")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="Wyoming")
        Membership.objects.create(person=person, organization=org)
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='deprecated',
                                          old_value='New York',
                                          new_value='Ma',
                                          category='address',
                                          alert='error',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='approved',
                                          old_value='New York',
                                          new_value='Maine',
                                          category='address',
                                          alert='error',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='rejected',
                                          old_value='Wyoming',
                                          new_value='W',
                                          category='address',
                                          alert='error',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='approved',
                                          old_value='Wyoming',
                                          new_value='WY',
                                          category='address',
                                          alert='error',
                                          applied_by='admin')
        setup_person_resolver()
        # getting updated object
        pc = PersonContactDetail.objects.filter(person=person)
        self.assertEqual(pc.filter(value="WY").count(), 1)
        self.assertEqual(pc.filter(value="Maine").count(), 1)

    def test_missing_voice_patches(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Missing Phone Number")
        Membership.objects.create(person=person, organization=org)
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='deprecated',
                                          new_value='321',
                                          category='voice',
                                          alert='warning',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='approved',
                                          new_value='456',
                                          category='voice',
                                          alert='warning',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='rejected',
                                          new_value='753',
                                          category='voice',
                                          alert='warning',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=jur,
                                          status='approved',
                                          new_value='852',
                                          category='voice',
                                          alert='warning',
                                          applied_by='user')
        DataQualityIssue.objects.create(content_object=person,
                                        jurisdiction=jur,
                                        alert='warning',
                                        issue='person-missing-phone')
        setup_person_resolver()
        # getting updated object
        pc = PersonContactDetail.objects.filter(person=person)
        self.assertEqual(pc.filter(value='456').count(), 1)
        self.assertEqual(pc.filter(value='852').count(), 1)
        # make sure that DataQualityIssue has been deleted
        dqi = DataQualityIssue.objects.filter(object_id=person.id)
        self.assertQuerysetEqual(dqi, [])

    def test_email_patches(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        org = Organization.objects.get(name="Democratic")
        person1 = Person.objects.create(name="Missing Email")
        person2 = Person.objects.create(name="Wrong Email")
        Membership.objects.create(person=person1, organization=org)
        Membership.objects.create(person=person2, organization=org)
        PersonContactDetail.objects.create(person=person2, type='email',
                                           value="wrong@gmail.com")
        IssueResolverPatch.objects.create(content_object=person1,
                                          jurisdiction=jur,
                                          status='deprecated',
                                          new_value='correct@gmail.com',
                                          category='email',
                                          alert='warning',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person1,
                                          jurisdiction=jur,
                                          status='approved',
                                          new_value='right@gmail.com',
                                          category='email',
                                          alert='warning',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person2,
                                          jurisdiction=jur,
                                          status='rejected',
                                          old_value='wrong@gmail.com',
                                          new_value='xyz@gmail.com',
                                          category='email',
                                          alert='error',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person2,
                                          jurisdiction=jur,
                                          status='approved',
                                          old_value='wrong@gmail.com',
                                          new_value='right@gmail.com',
                                          category='email',
                                          alert='error',
                                          applied_by='admin')
        DataQualityIssue.objects.create(content_object=person1,
                                        jurisdiction=jur,
                                        alert='warning',
                                        issue='person-missing-email')
        setup_person_resolver()
        # getting updated object
        pc1 = PersonContactDetail.objects.filter(person=person1)
        pc2 = PersonContactDetail.objects.filter(person=person2)
        self.assertEqual(pc1.filter(value='right@gmail.com').count(), 1)
        self.assertEqual(pc2.filter(value='right@gmail.com').count(), 1)
        # make sure that DataQualityIssue has been deleted
        dqi = DataQualityIssue.objects.filter(object_id=person1.id)
        self.assertQuerysetEqual(dqi, [])
