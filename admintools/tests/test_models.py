from django.test import TestCase
from admintools.models import DataQualityIssue, IssueResolverPatch
from django.utils import timezone
from opencivicdata.core.models import (Jurisdiction, Person, Division,
                                       Organization, Membership)
from pupa.models import RunPlan
from django.contrib.contenttypes.models import ContentType
from admintools.issues import IssueType


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

    def test_dataqualityissue_create(self):
        """
        To check that DataQualityIssue objects are getting created.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        person = Person.objects.create(name="Hitesh Garg")
        dqi = DataQualityIssue.objects.create(content_object=person,
                                              issue='missing-photo',
                                              alert='warning',
                                              jurisdiction=jur)
        self.assertEqual(dqi.issue, "missing-photo")
        self.assertEqual(dqi.alert, "warning")
        self.assertEqual(dqi.jurisdiction, jur)
        self.assertEqual(dqi.content_object, person)
        self.assertEqual(dqi.object_id, person.id)

    def test_dataqualityissue_content_type_id(self):
        """
        Two different class objects can't have same content_type_id
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        person = Person.objects.create(name="Hitesh Garg")
        org = Organization.objects.create(name="Test Org")
        DataQualityIssue.objects.create(content_object=person,
                                        issue='missing-photo',
                                        alert='warning',
                                        jurisdiction=jur)
        DataQualityIssue.objects.create(content_object=org,
                                        issue='no-memberships',
                                        alert='error',
                                        jurisdiction=jur)
        contenttype_obj_dqi1 = ContentType.objects.get_for_model(person)
        contenttype_obj_dqi2 = ContentType.objects.get_for_model(org)
        self.assertNotEqual(contenttype_obj_dqi1.id, contenttype_obj_dqi2.id)

    def test_dataqualityissue_issue_choices(self):
        """
        Issue choices must be updated on the DB migrations
        """
        self.assertEqual(DataQualityIssue._meta.get_field('issue').choices,
                         IssueType.choices())


class IssueResolverPatchModelTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )

    def test_patch_create(self):
        """
        To check that Patch objects are getting created.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        person = Person.objects.create(name="Hitesh Garg")
        org = Organization.objects.create(name="Democratic", jurisdiction=jur)
        Membership.objects.create(person=person, organization=org)
        patch = IssueResolverPatch.objects.create(content_object=person,
                                                  jurisdiction=jur,
                                                  status='alert',
                                                  old_value='test_old',
                                                  new_value='test_new',
                                                  category='address',
                                                  note='some note',
                                                  source='http://www.test.com',
                                                  reporter_name='HTSG',
                                                  reporter_email='te@mail.com',
                                                  applied_by='admin')
        self.assertEqual(patch.jurisdiction, jur)
        self.assertEqual(patch.status, 'alert')
        self.assertEqual(patch.old_value, 'test_old')
        self.assertEqual(patch.new_value, 'test_new')
        self.assertEqual(patch.category, 'address')
        self.assertEqual(patch.note, 'some note')
        self.assertEqual(patch.source, 'http://www.test.com')
        self.assertEqual(patch.reporter_name, 'HTSG')
        self.assertEqual(patch.reporter_email, 'te@mail.com')
        self.assertEqual(patch.applied_by, 'admin')
