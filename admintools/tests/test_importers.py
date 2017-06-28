from django.test import TestCase
from admintools.models import DataQualityIssue
from opencivicdata.core.models import (Jurisdiction, Person, Division,
                                       Organization, Membership)
from opencivicdata.legislative.models import (Bill, VoteEvent, BillSponsorship,
                                              LegislativeSession, PersonVote,
                                              VoteCount)
from admintools.importers import (person_issues, orgs_issues, bills_issues,
                                  vote_event_issues)


class PeopleImportersTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )

        p = Person.objects.create(name="Hitesh Garg")
        org = Organization.objects.create(name="test org", jurisdiction=jur)
        Membership.objects.create(person=p, organization=org)

    def test_people_importer_missing_photo(self):
        person_issues()
        person = Person.objects.get(name="Hitesh Garg")
        h = DataQualityIssue.objects.filter(object_id=person.id,
                                            issue='person-missing-photo')
        self.assertEqual(len(h), 1)

    def test_people_importer_missing_email(self):
        person_issues()
        person = Person.objects.get(name="Hitesh Garg")
        h = DataQualityIssue.objects.filter(object_id=person.id,
                                            issue='person-missing-email')
        self.assertEqual(len(h), 1)

    def test_people_importer_missing_phone(self):
        person_issues()
        person = Person.objects.get(name="Hitesh Garg")
        h = DataQualityIssue.objects.filter(object_id=person.id,
                                            issue='person-missing-phone')
        self.assertEqual(len(h), 1)

    def test_people_importer_missing_address(self):
        person_issues()
        person = Person.objects.get(name="Hitesh Garg")
        h = DataQualityIssue.objects.filter(object_id=person.id,
                                            issue='person-missing-address')
        self.assertEqual(len(h), 1)


class OrganizationImportersTests(TestCase):

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
                id="ocd-division/country:us/state:ds",
                name="Dausa State Senate",
                url="http://www.senate.ds.gov",
                division=division,
            )
        # For `no-memberships`
        Organization.objects.create(name="test org1", jurisdiction=jur1)
        # For `unmatched-person-memberships`
        org2 = Organization.objects.create(name="test org2", jurisdiction=jur2)
        Membership.objects.create(person_name='Unmatched Person',
                                  organization=org2)

    def test_org_importer_no_memberships(self):
        orgs_issues()
        org = Organization.objects.get(name="test org1")
        h = DataQualityIssue.objects \
            .filter(object_id=org.id, issue='organization-no-memberships')
        self.assertEqual(len(h), 1)

    def test_org_importer_membership_unmatched_person(self):
        orgs_issues()
        mem = Membership.objects.get(person_name='Unmatched Person')
        h = DataQualityIssue.objects \
            .filter(object_id=mem.id, issue='membership-unmatched-person')
        self.assertEqual(len(h), 1)


class BillsImportersTests(TestCase):
    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        ls = LegislativeSession.objects.create(jurisdiction=jur,
                                               identifier="test ls",
                                               name="Test Session",
                                               start_date="2017-06-25",
                                               end_date="2017-06-26")
        # For `no-sponsors`
        Bill.objects.create(legislative_session=ls, identifier="test bill1")
        # For `no-actions` & `no-versions`
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="test bill")
        # For `unmatched-person-sponsor`
        BillSponsorship.objects.create(bill=bill, classification="Test1",
                                       name="Test Name1", entity_type='person')
        # For `unmatched-org-sponsor`
        BillSponsorship.objects.create(bill=bill, classification="Test2",
                                       name="Test Name2",
                                       entity_type='organization')

    def test_bill_importer_no_actions(self):
        bills_issues()
        bill = Bill.objects.get(identifier="test bill")
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-no-actions')
        self.assertEqual(len(h), 1)

    def test_bill_importer_no_sponsors(self):
        bills_issues()
        bill = Bill.objects.get(identifier="test bill1")
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-no-sponsors')
        self.assertEqual(len(h), 1)

    def test_bill_importer_no_versions(self):
        bills_issues()
        bill = Bill.objects.get(identifier="test bill")
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-no-versions')
        self.assertEqual(len(h), 1)

    def test_bill_importer_unmatched_org_sponsor(self):
        bills_issues()
        bill = Bill.objects.get(identifier="test bill")
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-unmatched-org-sponsor')
        self.assertEqual(len(h), 1)

    def test_bill_importer_unmatched_person_sponsor(self):
        bills_issues()
        bill = Bill.objects.get(identifier="test bill")
        h = DataQualityIssue.objects \
            .filter(object_id=bill.id, issue='bill-unmatched-person-sponsor')
        self.assertEqual(len(h), 1)


class VoteEventImportersTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        ls = LegislativeSession.objects.create(jurisdiction=jur,
                                               identifier="test ls",
                                               name="Test Session",
                                               start_date="2017-06-25",
                                               end_date="2017-06-26")
        org = Organization.objects.create(name="test org1", jurisdiction=jur)
        # For `missing-voters`
        VoteEvent.objects.create(identifier="vote1", motion_text="Test",
                                 start_date="2017-06-26",
                                 result='pass', legislative_session=ls,
                                 organization=org)
        # For `missing-bill`
        vote2 = VoteEvent.objects \
            .create(identifier="vote2", motion_text="Test",
                    start_date="2017-06-26",
                    result='pass', legislative_session=ls,
                    organization=org)
        # For `unmatched-voter`
        PersonVote.objects.create(vote_event=vote2, option='yes',
                                  voter_name="Test Voter")
        # For `missing-counts`
        VoteCount.objects.create(vote_event=vote2, option='yes', value=0)
        VoteCount.objects.create(vote_event=vote2, option='no', value=0)
        # For `bad-counts`
        VoteCount.objects.create(vote_event=vote2, option='other', value=10)

    def test_voteevent_importer_missing_voters(self):
        vote_event_issues()
        voteevent = VoteEvent.objects.get(identifier="vote1")
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-missing-voters')
        self.assertEqual(len(h), 1)

    def test_voteevent_importer_missing_bill(self):
        vote_event_issues()
        voteevent = VoteEvent.objects.get(identifier="vote2")
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-missing-bill')
        self.assertEqual(len(h), 1)

    def test_voteevent_importer_unmatched_voter(self):
        vote_event_issues()
        voteevent = VoteEvent.objects.get(identifier="vote2")
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-unmatched-voter')
        self.assertEqual(len(h), 1)

    def test_voteevent_importer_missing_counts(self):
        vote_event_issues()
        voteevent = VoteEvent.objects.get(identifier="vote2")
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-missing-counts')
        self.assertEqual(len(h), 1)

    def test_voteevent_importer_bad_counts(self):
        vote_event_issues()
        voteevent = VoteEvent.objects.get(identifier="vote2")
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-bad-counts')
        self.assertEqual(len(h), 1)
