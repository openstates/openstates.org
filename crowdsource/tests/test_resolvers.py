import sys
from django.test import TestCase
from django.utils.six import StringIO
from opencivicdata.core.models import (Person, Jurisdiction, Division,
                                       Organization, Membership,
                                       PersonContactDetail)
from dataquality.models import IssueResolverPatch, DataQualityIssue
from crowdsource.resolvers.person import apply_person_patches


class PeoplePatchesTest(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        self.jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )

    def test_name_patches(self):
        person = Person.objects.create(name="Wrong Name")
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='deprecated',
                                          old_value='Wrong Name',
                                          new_value='Garg',
                                          category='name',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='rejected',
                                          old_value='Wrong Name',
                                          new_value='Hitesh',
                                          category='name',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='Wrong Name',
                                          new_value='Hitesh Garg',
                                          category='name',
                                          applied_by='admin')
        apply_person_patches(self.jur.name)
        # getting updated object
        p = Person.objects.get(id=person.id)
        self.assertEqual(p.name, "Hitesh Garg")

    def test_image_patches(self):
        person = Person.objects.create(name="Wrong Image",
                                       image="http://www.image.png")
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='rejected',
                                          old_value='http://www.image.png',
                                          new_value='http://www.ht.png',
                                          category='image',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='deprecated',
                                          old_value='http://www.image.png',
                                          new_value='http://www.rt.png',
                                          category='image',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='http://www.image.png',
                                          new_value='http://www.right.png',
                                          category='image',
                                          applied_by='admin')
        apply_person_patches(self.jur.name)
        # getting updated object
        p = Person.objects.get(id=person.id)
        self.assertEqual(p.image, "http://www.right.png")

    def test_address_patches(self):
        person = Person.objects.create(name="Wrong Address")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="New York")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="Wyoming")
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='deprecated',
                                          old_value='New York',
                                          new_value='Ma',
                                          category='address',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='New York',
                                          new_value='Maine',
                                          category='address',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='rejected',
                                          old_value='Wyoming',
                                          new_value='W',
                                          category='address',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='Wyoming',
                                          new_value='WY',
                                          category='address',
                                          applied_by='admin')
        apply_person_patches(self.jur.name)
        # getting updated object
        pc = PersonContactDetail.objects.filter(person=person)
        self.assertEqual(pc.filter(value="WY").count(), 1)
        self.assertEqual(pc.filter(value="Maine").count(), 1)

    def test_missing_voice_patches(self):
        person = Person.objects.create(name="Missing Phone Number")
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='deprecated',
                                          new_value='321',
                                          category='voice',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          new_value='456',
                                          category='voice',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='rejected',
                                          new_value='753',
                                          category='voice',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          new_value='852',
                                          category='voice',
                                          applied_by='user')
        apply_person_patches(self.jur.name)
        # getting updated object
        pc = PersonContactDetail.objects.filter(person=person)
        self.assertEqual(pc.filter(value='456').count(), 1)
        self.assertEqual(pc.filter(value='852').count(), 1)
    
    def test_wrong_voice_patches(self):
        person = Person.objects.create(name="Missing Phone Number")
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value='654')
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value='258')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='deprecated',
                                          old_value='654',
                                          new_value='321',
                                          category='voice',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='654',
                                          new_value='456',
                                          category='voice',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='rejected',
                                          old_value='258',
                                          new_value='753',
                                          category='voice',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='258',
                                          new_value='852',
                                          category='voice',
                                          applied_by='user')
        apply_person_patches(self.jur.name)
        # getting updated object
        pc = PersonContactDetail.objects.filter(person=person)
        self.assertEqual(pc.filter(value='456').count(), 1)
        self.assertEqual(pc.filter(value='852').count(), 1)

    def test_email_patches(self):
        person1 = Person.objects.create(name="Missing Email")
        person2 = Person.objects.create(name="Wrong Email")
        PersonContactDetail.objects.create(person=person2, type='email',
                                           value="wrong@gmail.com")
        IssueResolverPatch.objects.create(content_object=person1,
                                          jurisdiction=self.jur,
                                          status='deprecated',
                                          new_value='correct@gmail.com',
                                          category='email',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person1,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          new_value='right@gmail.com',
                                          category='email',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person2,
                                          jurisdiction=self.jur,
                                          status='rejected',
                                          old_value='wrong@gmail.com',
                                          new_value='xyz@gmail.com',
                                          category='email',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person2,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='wrong@gmail.com',
                                          new_value='right@gmail.com',
                                          category='email',
                                          applied_by='admin')
        apply_person_patches(self.jur.name)
        # getting updated object
        pc1 = PersonContactDetail.objects.filter(person=person1)
        pc2 = PersonContactDetail.objects.filter(person=person2)
        self.assertEqual(pc1.filter(value='right@gmail.com').count(), 1)
        self.assertEqual(pc2.filter(value='right@gmail.com').count(), 1)
        
    def test_name_patch_over_ride_scraper(self):
        person = Person.objects.create(name="Wrong Name")
        # This test is basically only for approved Resolver
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='Wrong Name',
                                          new_value='Right Name',
                                          category='name',
                                          applied_by='admin')
        # Scraper ran and updated name to 'Right-Name'
        person.name = 'Right-Name' # Notice the hyphen in b/w
        person.save()
        apply_person_patches(self.jur.name)
        # getting updated object
        p = Person.objects.get(id=person.id)
        resolver = IssueResolverPatch.objects.get(object_id=person.id,
                                                  category='name')
        DataQualityIssue.objects.get(object_id=person.id,
                                     message="Resolver over-ridden",
                                     issue='wrong-name')
        self.assertEqual(p.name, "Right-Name")
        self.assertEqual(resolver.status, 'deprecated')

    def test_image_patch_over_ride_scraper(self):
        person = Person.objects.create(name="Wrong Image",
                                       image="http://www.image.png")
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='http://www.image.png',
                                          new_value='http://www.right.png',
                                          category='image',
                                          applied_by='admin')
        # Scraper ran and updated image to the following
        person.image = 'http://www.newlyScraped.png' # Notice the hyphen in b/w
        person.save()
        apply_person_patches(self.jur.name)
        # getting updated object
        p = Person.objects.get(id=person.id)
        resolver = IssueResolverPatch.objects.get(object_id=person.id,
                                                  category='image')
        DataQualityIssue.objects.get(object_id=person.id,
                                     message="Resolver over-ridden",
                                     issue='wrong-photo')
        self.assertEqual(p.image, "http://www.newlyScraped.png")
        self.assertEqual(resolver.status, 'deprecated')

    # There are two approved patches, one gets over ridden by scraper 
    def test_address_patch_over_ride_scraper(self):
        person = Person.objects.create(name="Wrong Address")
        c = PersonContactDetail.objects.create(person=person, type='address',
                                               value="New York")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="Wyoming")
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='New York',
                                          new_value='Maine',
                                          category='address',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='Wyoming',
                                          new_value='WY',
                                          category='address',
                                          applied_by='admin')
        # Scraper Ran and updated 'New York' to 'New New York'
        c.value = "New New York"
        c.save()
        apply_person_patches(self.jur.name)
        # getting updated object
        pc = PersonContactDetail.objects.filter(person=person)
        self.assertEqual(pc.filter(value="WY").count(), 1)
        self.assertEqual(pc.filter(value="Maine").count(), 0)

        resolver = IssueResolverPatch.objects.get(object_id=person.id,
                                                  category='address',
                                                  old_value='New York')
        DataQualityIssue.objects.get(object_id=person.id,
                                     message="Resolver over-ridden",
                                     issue='wrong-address')

        self.assertEqual(resolver.status, 'deprecated')

    def test_wrong_voice_patch_over_ride_scraper(self):
        person = Person.objects.create(name="Missing Phone Number")
        c = PersonContactDetail.objects.create(person=person, type='voice',
                                               value='654')
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value='258')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='654',
                                          new_value='456',
                                          category='voice',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='258',
                                          new_value='852',
                                          category='voice',
                                          applied_by='user')
        # Scraper Ran and updated '654' to '655'
        c.value = '655'
        c.save()
        apply_person_patches(self.jur.name)
        # getting updated object
        pc = PersonContactDetail.objects.filter(person=person)
        self.assertEqual(pc.filter(value='456').count(), 0)
        self.assertEqual(pc.filter(value='852').count(), 1)

        resolver = IssueResolverPatch.objects.get(object_id=person.id,
                                                  category='voice',
                                                  old_value='654')
        DataQualityIssue.objects.get(object_id=person.id,
                                     message="Resolver over-ridden",
                                     issue='wrong-phone')

        self.assertEqual(resolver.status, 'deprecated')

    def test_wrong_email_patch_over_ride_scraper(self):
        person1 = Person.objects.create(name="Missing Email")
        person2 = Person.objects.create(name="Wrong Email")
        PersonContactDetail.objects.create(person=person1, type='email',
                                           value="wrong1@gmail.com")
        c = PersonContactDetail.objects.create(person=person2, type='email',
                                               value="wrong2@gmail.com")
        IssueResolverPatch.objects.create(content_object=person1,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='wrong1@gmail.com',
                                          new_value='right1@gmail.com',
                                          category='email',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=person2,
                                          jurisdiction=self.jur,
                                          status='approved',
                                          old_value='wrong2@gmail.com',
                                          new_value='right2@gmail.com',
                                          category='email',
                                          applied_by='admin')
        # Scraper Ran and updated '654' to '655'
        c.value = 'rightscraped@gmail.com'
        c.save()
        apply_person_patches(self.jur.name)
        # getting updated object
        pc1 = PersonContactDetail.objects.filter(person=person1)
        pc2 = PersonContactDetail.objects.filter(person=person2)
        self.assertEqual(pc1.filter(value='right1@gmail.com').count(), 1)
        self.assertEqual(pc2.filter(value='rightscraped@gmail.com').count(), 1)

        resolver = IssueResolverPatch.objects.get(object_id=person2.id,
                                                  category='email')
        DataQualityIssue.objects.get(object_id=person2.id,
                                     message="Resolver over-ridden",
                                     issue='wrong-email')

        self.assertEqual(resolver.status, 'deprecated')
