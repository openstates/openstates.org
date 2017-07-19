import sys
from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from admintools.issues import IssueType
from admintools.models import DataQualityIssue
from opencivicdata.core.models import (Jurisdiction, Person, Division,
                                       Organization, Membership,
                                       PersonContactDetail)
from opencivicdata.legislative.models import (Bill, VoteEvent,
                                              LegislativeSession)
from admintools.importers import (person_issues, orgs_issues, bills_issues,
                                  vote_event_issues)


class CommandsTestCase(TestCase):
    "Test `import all` commands"

    def test_import_all_command(self):
        out = StringIO()
        sys.stout = out
        args = ['all']
        call_command('import', *args, stdout=out)
        self.assertIn('Successfully Imported People DataQualityIssues into DB',
                      out.getvalue())
        self.assertIn(
            'Successfully Imported Organization DataQualityIssues into DB',
            out.getvalue())
        self.assertIn(
            'Successfully Imported VoteEvent DataQualityIssues into DB',
            out.getvalue())
        self.assertIn(
            'Successfully Imported Bill DataQualityIssues into DB',
            out.getvalue())

    def test_import_all_people_command(self):
        out = StringIO()
        sys.stout = out
        args = ['all']
        opts = {'people': True}
        call_command('import', *args, **opts, stdout=out)
        self.assertIn('Successfully Imported People DataQualityIssues into DB',
                      out.getvalue())

    def test_import_all_organization_command(self):
        out = StringIO()
        sys.stout = out
        args = ['all']
        opts = {'organization': True}
        call_command('import', *args, **opts, stdout=out)
        self.assertIn(
            'Successfully Imported Organization DataQualityIssues into DB',
            out.getvalue())

    def test_import_all_vote_event_command(self):
        out = StringIO()
        sys.stout = out
        args = ['all']
        opts = {'vote_event': True}
        call_command('import', *args, **opts, stdout=out)
        self.assertIn(
            'Successfully Imported VoteEvent DataQualityIssues into DB',
            out.getvalue())

    def test_import_all_bill_command(self):
        out = StringIO()
        sys.stout = out
        args = ['all']
        opts = {'bills': True}
        call_command('import', *args, **opts, stdout=out)
        self.assertIn(
            'Successfully Imported Bill DataQualityIssues into DB',
            out.getvalue())


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

        Organization.objects.create(name="Democratic", jurisdiction=jur)

    def test_people_importer_missing_photo(self):
        org = Organization.objects.get(name="Democratic")

        person = Person.objects.create(name="Missing Photo")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="New York")
        PersonContactDetail.objects.create(person=person, type='email',
                                           value="person@email.com")
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value="1234567890")
        Membership.objects.create(person=person, organization=org)

        # To check that on running importer twice no duplicate DataQualityIssue
        # are being created.
        person_issues()
        person_issues()

        mp = DataQualityIssue.objects.filter(issue='person-missing-photo')
        rest = DataQualityIssue.objects.exclude(issue='person-missing-photo')

        self.assertEqual(len(mp), 1)
        self.assertQuerysetEqual(rest, [])

    def test_people_importer_missing_email(self):
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Missing Email",
                                       image="http://personimage.png")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="New York")
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value="1234567890")

        Membership.objects.create(person=person, organization=org)

        person_issues()

        me = DataQualityIssue.objects.filter(issue='person-missing-email')
        rest = DataQualityIssue.objects.exclude(issue='person-missing-email')
        self.assertEqual(len(me), 1)
        self.assertQuerysetEqual(rest, [])

    def test_people_importer_missing_phone(self):
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Missing Phone",
                                       image="http://personimage.png")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="New York")
        PersonContactDetail.objects.create(person=person, type='email',
                                           value="person@email.com")

        Membership.objects.create(person=person, organization=org)

        person_issues()

        mp = DataQualityIssue.objects.filter(issue='person-missing-phone')
        rest = DataQualityIssue.objects.exclude(issue='person-missing-phone')
        self.assertEqual(len(mp), 1)
        self.assertQuerysetEqual(rest, [])

    def test_people_importer_missing_address(self):
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Missing Address",
                                       image="http://personimage.png")
        PersonContactDetail.objects.create(person=person, type='email',
                                           value="person@email.com")
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value="1234567890")

        Membership.objects.create(person=person, organization=org)

        person_issues()

        ma = DataQualityIssue.objects.filter(issue='person-missing-address')
        rest = DataQualityIssue.objects.exclude(issue='person-missing-address')
        self.assertEqual(len(ma), 1)
        self.assertQuerysetEqual(rest, [])

    def test_people_importer_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-name', 'Missing Name', 'person', 'error')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-name', 'Missing Name'))
        try:
            person_issues()
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'People Importer needs'
                             ' update for new issue.')
        self.assertEqual(exception_raised, True)


class OrganizationImportersTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )

    def test_org_importer_no_memberships(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        Organization.objects.create(name="No Membership", jurisdiction=jur)

        # To check that on running importer twice no duplicate DataQualityIssue
        # are being created.
        orgs_issues()
        orgs_issues()

        nm = DataQualityIssue.objects.filter(
            issue='organization-no-memberships').count()
        rest = DataQualityIssue.objects.exclude(
            issue='organization-no-memberships')
        self.assertEqual(nm, 1)
        self.assertQuerysetEqual(rest, [])

    def test_org_importer_membership_unmatched_person(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="Unmatched Person Memberships",
                                          jurisdiction=jur)
        Membership.objects.create(person_name='Unmatched Person',
                                  organization=org)
        orgs_issues()
        rest = DataQualityIssue.objects.exclude(
            issue='membership-unmatched-person')
        up = DataQualityIssue.objects.filter(
            issue='membership-unmatched-person').count()
        self.assertQuerysetEqual(rest, [])
        self.assertEqual(up, 1)

    def test_org_importer_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-orgs', 'Missing Orgs', 'organization', 'error')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-orgs', 'Missing Orgs'))
        try:
            orgs_issues()
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Organization Importer needs '
                             'update for new issue.')
        self.assertEqual(exception_raised, True)


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
        LegislativeSession.objects.create(jurisdiction=jur,
                                          identifier="2017",
                                          name="2017 Test Session",
                                          start_date="2017-06-25",
                                          end_date="2017-06-26")

    def test_bill_importer_no_actions(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="Org for Bill with no actions",
                                          jurisdiction=jur)
        p = Person.objects.create(name="Person for Bill with no actions")
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill with No Actions")
        bill.versions.create(note="Bill with version",
                             date="2017-06-28")
        bill.sponsorships \
            .create(classification="Bill with matched person sponsor",
                    name="matched Person Sponsor", entity_type='person',
                    person=p)
        bill.sponsorships \
            .create(classification="Bill with matched organization sponsor",
                    name="matched Organization Sponsor", organization=org,
                    entity_type='organization')

        # To check that on running importer twice no duplicate DataQualityIssue
        # are being created.
        bills_issues()
        bills_issues()

        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-no-actions').count()
        rest = DataQualityIssue.objects.exclude(object_id=bill.id,
                                                issue='bill-no-actions')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_importer_no_sponsors(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="Org for Bill with no sponsor",
                                          jurisdiction=jur)
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill with No Sponsors")
        bill.actions.create(description="Bill with Action", organization=org,
                            date="2017-06-28", order=2)
        bill.versions.create(note="Bill with version",
                             date="2017-06-28")
        bills_issues()
        h = DataQualityIssue.objects.filter(issue='bill-no-sponsors').count()
        rest = DataQualityIssue.objects.exclude(issue='bill-no-sponsors')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_importer_no_versions(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="Org for Bill with no versions",
                                          jurisdiction=jur)
        p = Person.objects.create(name="Person for Bill with no versions")
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill with No Versions")
        bill.actions.create(description="Bill with Action", organization=org,
                            date="2017-06-28", order=2)
        bill.sponsorships \
            .create(classification="Bill with matched person sponsor",
                    name="matched Person Sponsor", entity_type='person',
                    person=p)
        bill.sponsorships \
            .create(classification="Bill with matched organization sponsor",
                    name="matched Organization Sponsor", organization=org,
                    entity_type='organization')
        bills_issues()
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-no-versions').count()
        rest = DataQualityIssue.objects.exclude(issue='bill-no-versions')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_importer_unmatched_org_sponsor(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="Org for Unmatched org sponsor",
                                          jurisdiction=jur)
        p = Person.objects.create(name="Person for Unmatched org sponsor")
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill: Unmatched org sponsor")
        bill.actions.create(description="Bill with Action", organization=org,
                            date="2017-06-28", order=2)
        bill.versions.create(note="Bill with version",
                             date="2017-06-28")
        bill.sponsorships \
            .create(classification="Bill with matched person sponsor",
                    name="matched Person Sponsor", entity_type='person',
                    person=p)
        bill.sponsorships \
            .create(classification="Bill with matched organization sponsor",
                    name="matched Organization Sponsor",
                    entity_type='organization')
        bills_issues()
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-unmatched-org-sponsor')
        rest = DataQualityIssue.objects \
            .exclude(object_id=bill.id, issue='bill-unmatched-org-sponsor')

        self.assertEqual(len(h), 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_importer_unmatched_person_sponsor(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="Org: Unmatched person sponsor",
                                          jurisdiction=jur)
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill: Unmatched person sponsor")
        bill.actions.create(description="Bill with Action", organization=org,
                            date="2017-06-28", order=2)
        bill.versions.create(note="Bill with version",
                             date="2017-06-28")
        bill.sponsorships \
            .create(classification="Bill with unmatched person sponsor",
                    name="Unmatched Person Sponsor", entity_type='person')
        bill.sponsorships \
            .create(classification="Bill with matched organization sponsor",
                    name="matched Organization Sponsor", organization=org,
                    entity_type='organization')
        bills_issues()
        h = DataQualityIssue.objects \
            .filter(object_id=bill.id, issue='bill-unmatched-person-sponsor')
        rest = DataQualityIssue.objects \
            .exclude(object_id=bill.id, issue='bill-unmatched-person-sponsor')
        self.assertEqual(len(h), 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_importer_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-billxyz', 'Missing BillXYZ', 'bill', 'error')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-billxyz', 'Missing BillXYZ'))
        try:
            bills_issues()
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Bill Importer needs '
                             'update for new issue.')
        self.assertEqual(exception_raised, True)


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
                                               identifier="2017",
                                               name="2017 Test Session",
                                               start_date="2017-06-25",
                                               end_date="2017-06-26")
        Organization.objects.create(name="Democratic", jurisdiction=jur)
        Person.objects.create(name="Voter")
        Bill.objects.create(legislative_session=ls,
                            identifier="Bill for VoteEvent")

    def test_voteevent_importer_missing_voters(self):
        org = Organization.objects.get(name="Democratic")
        bill = Bill.objects.get(identifier="Bill for VoteEvent")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects \
            .create(identifier="vote1",
                    motion_text="VoteEvent with missing-voters",
                    start_date="2017-06-26",
                    result='pass', legislative_session=ls,
                    organization=org,
                    bill=bill)

        # To check that on running importer twice no duplicate DataQualityIssue
        # are being created.
        vote_event_issues()
        vote_event_issues()

        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-missing-voters').count()
        rest = DataQualityIssue.objects \
            .exclude(object_id=voteevent.id,
                     issue='voteevent-missing-voters')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_importer_missing_bill(self):
        org = Organization.objects.get(name="Democratic")
        p = Person.objects.get(name="Voter")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects \
            .create(identifier="vote1",
                    motion_text="VoteEvent with missing-bill",
                    start_date="2017-06-26",
                    result='pass', legislative_session=ls,
                    organization=org)
        voteevent.votes.create(option="yes", voter=p)
        voteevent.counts.create(option="yes", value=1)
        vote_event_issues()
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-missing-bill').count()
        rest = DataQualityIssue.objects \
            .exclude(object_id=voteevent.id,
                     issue='voteevent-missing-bill')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_importer_unmatched_voter(self):
        org = Organization.objects.get(name="Democratic")
        bill = Bill.objects.get(identifier="Bill for VoteEvent")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects \
            .create(identifier="vote1",
                    motion_text="VoteEvent with unmatched-voter",
                    start_date="2017-06-26",
                    result='pass', legislative_session=ls,
                    organization=org,
                    bill=bill)
        voteevent.votes.create(option="yes", voter_name="unmatched-voter")
        voteevent.counts.create(option="yes", value=1)
        vote_event_issues()
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-unmatched-voter').count()
        rest = DataQualityIssue.objects \
            .exclude(object_id=voteevent.id,
                     issue='voteevent-unmatched-voter')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_importer_missing_counts(self):
        org = Organization.objects.get(name="Democratic")
        p = Person.objects.get(name="Voter")
        bill = Bill.objects.get(identifier="Bill for VoteEvent")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects \
            .create(identifier="vote1",
                    motion_text="VoteEvent with missing-counts",
                    start_date="2017-06-26",
                    result='pass', legislative_session=ls,
                    organization=org,
                    bill=bill)
        voteevent.votes.create(option="other", voter=p)
        voteevent.counts.create(option="other", value=1)
        voteevent.counts.create(option="yes", value=0)
        voteevent.counts.create(option="no", value=0)
        vote_event_issues()
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-missing-counts').count()
        rest = DataQualityIssue.objects \
            .exclude(object_id=voteevent.id,
                     issue='voteevent-missing-counts')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_importer_bad_counts(self):
        org = Organization.objects.get(name="Democratic")
        p = Person.objects.get(name="Voter")
        bill = Bill.objects.get(identifier="Bill for VoteEvent")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects \
            .create(identifier="vote1",
                    motion_text="VoteEvent with bad-counts",
                    start_date="2017-06-26",
                    result='pass', legislative_session=ls,
                    organization=org,
                    bill=bill)
        voteevent.votes.create(option="yes", voter=p)
        voteevent.counts.create(option="yes", value=1)
        voteevent.counts.create(option="no", value=1)
        voteevent.counts.create(option="other", value=1)
        vote_event_issues()
        h = DataQualityIssue.objects \
            .filter(object_id=voteevent.id,
                    issue='voteevent-bad-counts').count()
        rest = DataQualityIssue.objects \
            .exclude(object_id=voteevent.id,
                     issue='voteevent-bad-counts')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_importer_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-votexyz', 'Missing VoteXYZ', 'voteevent', 'warning')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-votexyz', 'Missing VoteXYZ'))
        try:
            vote_event_issues()
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'VoteEvents Importer needs '
                             'update for new issue.')
        self.assertEqual(exception_raised, True)
