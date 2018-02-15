from django.test import TestCase
from admintools.issues import IssueType
from admintools.models import DataQualityIssue
from opencivicdata.core.models import (Jurisdiction, Person, Division,
                                       Organization, Membership, Post,
                                       PersonContactDetail)
from opencivicdata.legislative.models import (Bill, VoteEvent,
                                              LegislativeSession)
from admintools.reports import (people_report, organizations_report,
                                bills_report, vote_events_report,
                                posts_report, memberships_report)


class BaseReportTestCase(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        self.jur = Jurisdiction.objects.create(
            id="ocd-division/country:us/state:mo",
            name="Missouri State Senate",
            url="http://www.senate.mo.gov",
            division=division,
        )
        Organization.objects.create(name="Democratic", jurisdiction=self.jur)


class PeopleReportTests(BaseReportTestCase):

    def test_people_missing_photo(self):
        org = Organization.objects.get(name="Democratic")

        person = Person.objects.create(name="Missing Photo")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="New York")
        PersonContactDetail.objects.create(person=person, type='email',
                                           value="person@email.com")
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value="1234567890")
        Membership.objects.create(person=person, organization=org)

        # To check that on running twice no duplicate DataQualityIssue are being created.
        people_report(self.jur)
        people_report(self.jur)

        mp = DataQualityIssue.objects.filter(issue='person-missing-photo')
        rest = DataQualityIssue.objects.exclude(issue='person-missing-photo')

        self.assertEqual(len(mp), 1)
        self.assertQuerysetEqual(rest, [])

    def test_people_missing_email(self):
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Missing Email",
                                       image="http://personimage.png")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="New York")
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value="1234567890")

        Membership.objects.create(person=person, organization=org)

        people_report(self.jur)

        me = DataQualityIssue.objects.filter(issue='person-missing-email')
        rest = DataQualityIssue.objects.exclude(issue='person-missing-email')
        self.assertEqual(len(me), 1)
        self.assertQuerysetEqual(rest, [])

    def test_people_missing_phone(self):
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Missing Phone",
                                       image="http://personimage.png")
        PersonContactDetail.objects.create(person=person, type='address',
                                           value="New York")
        PersonContactDetail.objects.create(person=person, type='email',
                                           value="person@email.com")

        Membership.objects.create(person=person, organization=org)

        people_report(self.jur)

        mp = DataQualityIssue.objects.filter(issue='person-missing-phone')
        rest = DataQualityIssue.objects.exclude(issue='person-missing-phone')
        self.assertEqual(len(mp), 1)
        self.assertQuerysetEqual(rest, [])

    def test_people_missing_address(self):
        org = Organization.objects.get(name="Democratic")
        person = Person.objects.create(name="Missing Address",
                                       image="http://personimage.png")
        PersonContactDetail.objects.create(person=person, type='email',
                                           value="person@email.com")
        PersonContactDetail.objects.create(person=person, type='voice',
                                           value="1234567890")

        Membership.objects.create(person=person, organization=org)

        people_report(self.jur)

        ma = DataQualityIssue.objects.filter(issue='person-missing-address')
        rest = DataQualityIssue.objects.exclude(issue='person-missing-address')
        self.assertEqual(len(ma), 1)
        self.assertQuerysetEqual(rest, [])

    def test_people_delete_active_dqis(self):
        org = Organization.objects.get(name="Democratic")
        p = Person.objects.create(name="John Snow")
        Membership.objects.create(person=p, organization=org)
        # Some Data Quality Issues
        DataQualityIssue.objects.create(jurisdiction=org.jurisdiction,
                                        content_object=p,
                                        alert='warning',
                                        issue='person-missing-phone',
                                        status='active')
        DataQualityIssue.objects.create(jurisdiction=org.jurisdiction,
                                        content_object=p,
                                        alert='warning',
                                        issue='person-missing-address',
                                        status='ignored')
        DataQualityIssue.objects.create(jurisdiction=org.jurisdiction,
                                        content_object=p,
                                        alert='warning',
                                        issue='person-missing-email',
                                        status='active')
        people_report(self.jur)

        ignored_issues = DataQualityIssue.objects.filter(
            status='ignored', issue='person-missing-address'
        )
        active_issues = DataQualityIssue.objects.filter(status='active')
        self.assertEqual(len(ignored_issues), 1)
        self.assertEqual(len(active_issues), 3)

    # `zzz` to make sure that this test runs at last. otherwise new IssueType
    # gets activated which cause other tests to raise ValueError.
    # tried deleting the created issue at end of test but not working.
    def test_people_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-name', 'Missing Name', 'person', 'error')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-name', 'Missing Name'))
        try:
            people_report(self.jur)
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'People Importer needs update for new issue.')
        self.assertEqual(exception_raised, True)


class OrganizationReportTests(BaseReportTestCase):

    def test_org_no_memberships(self):
        Organization.objects.create(name="No Membership", jurisdiction=self.jur)

        # To check that on running twice no duplicate DataQualityIssue are being created.
        organizations_report(self.jur)
        organizations_report(self.jur)

        nm = DataQualityIssue.objects.filter(issue='organization-no-memberships').count()
        rest = DataQualityIssue.objects.exclude(issue='organization-no-memberships')
        self.assertEqual(nm, 1)
        self.assertQuerysetEqual(rest, [])

    def test_org_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-orgs', 'Missing Orgs', 'organization', 'error')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-orgs', 'Missing Orgs'))
        try:
            organizations_report(self.jur)
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Organizations Importer needs update for new issue.')
        self.assertEqual(exception_raised, True)

    def test_org_delete_active_dqis(self):
        org1 = Organization.objects.create(name="No Membership1", jurisdiction=self.jur)
        org = Organization.objects.create(name="No Membership", jurisdiction=self.jur)
        # Some Data Quality Issues
        DataQualityIssue.objects.create(jurisdiction=self.jur,
                                        content_object=org1,
                                        alert='error',
                                        issue='organization-no-memberships',
                                        status='ignored')
        DataQualityIssue.objects.create(jurisdiction=self.jur,
                                        content_object=org,
                                        alert='error',
                                        issue='organization-no-memberships',
                                        status='active')
        organizations_report(self.jur)

        ignored_issues = DataQualityIssue.objects.filter(
            status='ignored', issue='organization-no-memberships'
        )
        active_issues = DataQualityIssue.objects.filter(status='active')
        self.assertEqual(len(ignored_issues), 1)
        self.assertEqual(len(active_issues), 1)


class MembershipsReportTests(BaseReportTestCase):

    def test_membership_unmatched_person(self):
        org = Organization.objects.create(name="Unmatched Person Memberships",
                                          jurisdiction=self.jur)
        Membership.objects.create(person_name='Unmatched Person', organization=org)
        memberships_report(self.jur)
        rest = DataQualityIssue.objects.exclude(issue='membership-unmatched-person')
        up = DataQualityIssue.objects.filter(issue='membership-unmatched-person').count()
        self.assertQuerysetEqual(rest, [])
        self.assertEqual(up, 1)

    def test_membership_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-mem', 'Missing Mem', 'membership', 'error')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-mem', 'Missing Mem'))
        try:
            memberships_report(self.jur)
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Memberships Importer needs update for new issue.')
        self.assertEqual(exception_raised, True)

    def test_membership_delete_active_dqis(self):
        org1 = Organization.objects.create(name="Test Org1",
                                           jurisdiction=self.jur)
        org = Organization.objects.create(name="Test Org",
                                          jurisdiction=self.jur)
        mem1 = Membership.objects.create(person_name='Unmatched Person1',
                                         organization=org)
        mem2 = Membership.objects.create(person_name='Unmatched Person2',
                                         organization=org1)
        # Some Data Quality Issues
        DataQualityIssue.objects.create(jurisdiction=self.jur,
                                        content_object=mem1,
                                        alert='warning',
                                        issue='membership-unmatched-person',
                                        status='ignored')
        DataQualityIssue.objects.create(jurisdiction=self.jur,
                                        content_object=mem2,
                                        alert='warning',
                                        issue='membership-unmatched-person',
                                        status='active')
        memberships_report(self.jur)

        ignored_issues = DataQualityIssue.objects.filter(status='ignored',
                                                         issue='membership-unmatched-person')
        active_issues = DataQualityIssue.objects.filter(status='active')
        self.assertEqual(len(ignored_issues), 1)
        self.assertEqual(len(active_issues), 1)


class PostsReportTests(BaseReportTestCase):

    def test_post_many_memberships(self):
        org = Organization.objects.create(name="Too Many Memberships", jurisdiction=self.jur)
        person = Person.objects.create(name="Test Person")
        post = Post.objects.create(label='14', organization=org,
                                   maximum_memberships=2)
        Membership.objects.create(person=person, organization=org,
                                  post=post)
        Membership.objects.create(person=person, organization=org,
                                  post=post)
        Membership.objects.create(person=person, organization=org,
                                  post=post)
        posts_report(self.jur)
        rest = DataQualityIssue.objects.exclude(
            issue='post-many-memberships')
        mm = DataQualityIssue.objects.filter(
            issue='post-many-memberships').count()
        self.assertQuerysetEqual(rest, [])
        self.assertEqual(mm, 1)

    def test_post_few_memberships(self):
        org = Organization.objects.create(name="Too Few Memberships",
                                          jurisdiction=self.jur)
        person = Person.objects.create(name="Test Person")
        post = Post.objects.create(label='14', organization=org,
                                   maximum_memberships=4)
        Membership.objects.create(person=person, organization=org,
                                  post=post)
        Membership.objects.create(person=person, organization=org,
                                  post=post)
        Membership.objects.create(person=person, organization=org,
                                  post=post)
        posts_report(self.jur)
        rest = DataQualityIssue.objects.exclude(
            issue='post-few-memberships')
        fm = DataQualityIssue.objects.filter(
            issue='post-few-memberships').count()
        self.assertQuerysetEqual(rest, [])
        self.assertEqual(fm, 1)

    def test_post_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-posts', 'Missing Posts', 'post', 'error')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-posts', 'Missing Posts'))
        try:
            posts_report(self.jur)
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Posts Importer needs update for new issue.')
        self.assertEqual(exception_raised, True)


class BillsReportTests(BaseReportTestCase):
    def setUp(self):
        super().setUp()
        LegislativeSession.objects.create(jurisdiction=self.jur,
                                          identifier="2017",
                                          name="2017 Test Session",
                                          start_date="2017-06-25",
                                          end_date="2017-06-26")

    def test_bill_no_actions(self):
        org = Organization.objects.create(name="Org for Bill with no actions",
                                          jurisdiction=self.jur)
        p = Person.objects.create(name="Person for Bill with no actions")
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill with No Actions")
        bill.versions.create(note="Bill with version",
                             date="2017-06-28")
        bill.sponsorships.create(classification="Bill with matched person sponsor",
                                 name="matched Person Sponsor", entity_type='person',
                                 person=p)
        bill.sponsorships.create(classification="Bill with matched organization sponsor",
                                 name="matched Organization Sponsor", organization=org,
                                 entity_type='organization')

        # To check that on running twice no duplicate DataQualityIssue are being created.
        bills_report(self.jur)
        bills_report(self.jur)

        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-no-actions').count()
        rest = DataQualityIssue.objects.exclude(object_id=bill.id,
                                                issue='bill-no-actions')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_no_sponsors(self):
        org = Organization.objects.create(name="Org for Bill with no sponsor",
                                          jurisdiction=self.jur)
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill with No Sponsors")
        bill.actions.create(description="Bill with Action", organization=org,
                            date="2017-06-28", order=2)
        bill.versions.create(note="Bill with version",
                             date="2017-06-28")
        bills_report(self.jur)
        h = DataQualityIssue.objects.filter(issue='bill-no-sponsors').count()
        rest = DataQualityIssue.objects.exclude(issue='bill-no-sponsors')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_no_versions(self):
        org = Organization.objects.create(name="Org for Bill with no versions",
                                          jurisdiction=self.jur)
        p = Person.objects.create(name="Person for Bill with no versions")
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill with No Versions")
        bill.actions.create(description="Bill with Action", organization=org,
                            date="2017-06-28", order=2)
        bill.sponsorships.create(classification="Bill with matched person sponsor",
                                 name="matched Person Sponsor", entity_type='person',
                                 person=p)
        bill.sponsorships.create(classification="Bill with matched organization sponsor",
                                 name="matched Organization Sponsor", organization=org,
                                 entity_type='organization')
        bills_report(self.jur)
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-no-versions').count()
        rest = DataQualityIssue.objects.exclude(issue='bill-no-versions')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_unmatched_org_sponsor(self):
        org = Organization.objects.create(name="Org for Unmatched org sponsor",
                                          jurisdiction=self.jur)
        p = Person.objects.create(name="Person for Unmatched org sponsor")
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill: Unmatched org sponsor")
        bill.actions.create(description="Bill with Action", organization=org,
                            date="2017-06-28", order=2)
        bill.versions.create(note="Bill with version",
                             date="2017-06-28")
        bill.sponsorships.create(classification="Bill with matched person sponsor",
                                 name="matched Person Sponsor", entity_type='person',
                                 person=p)
        bill.sponsorships.create(classification="Bill with matched organization sponsor",
                                 name="matched Organization Sponsor",
                                 entity_type='organization')
        bills_report(self.jur)
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-unmatched-org-sponsor')
        rest = DataQualityIssue.objects.exclude(
            object_id=bill.id, issue='bill-unmatched-org-sponsor')

        self.assertEqual(len(h), 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_unmatched_person_sponsor(self):
        org = Organization.objects.create(name="Org: Unmatched person sponsor",
                                          jurisdiction=self.jur)
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill: Unmatched person sponsor")
        bill.actions.create(description="Bill with Action", organization=org,
                            date="2017-06-28", order=2)
        bill.versions.create(note="Bill with version",
                             date="2017-06-28")
        bill.sponsorships.create(classification="Bill with unmatched person sponsor",
                                 name="Unmatched Person Sponsor", entity_type='person')
        bill.sponsorships.create(classification="Bill with matched organization sponsor",
                                 name="matched Organization Sponsor", organization=org,
                                 entity_type='organization')
        bills_report(self.jur)
        h = DataQualityIssue.objects.filter(object_id=bill.id,
                                            issue='bill-unmatched-person-sponsor')
        rest = DataQualityIssue.objects.exclude(object_id=bill.id,
                                                issue='bill-unmatched-person-sponsor')
        self.assertEqual(len(h), 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_delete_active_dqis(self):
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="BS01")
        # Some Data Quality Issues
        DataQualityIssue.objects.create(jurisdiction=self.jur,
                                        content_object=bill,
                                        alert='error',
                                        issue='bill-no-actions',
                                        status='ignored')
        DataQualityIssue.objects.create(jurisdiction=self.jur,
                                        content_object=bill,
                                        alert='warning',
                                        issue='bill-no-sponsors',
                                        status='active')
        DataQualityIssue.objects.create(jurisdiction=self.jur,
                                        content_object=bill,
                                        alert='warning',
                                        issue='bill-no-versions',
                                        status='active')
        bills_report(self.jur)
        ignored_issues = DataQualityIssue.objects.filter(status='ignored',
                                                         issue='bill-no-actions')
        active_issues = DataQualityIssue.objects.filter(status='active')
        self.assertEqual(len(ignored_issues), 1)
        self.assertEqual(len(active_issues), 2)

    def test_bill_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-billxyz', 'Missing BillXYZ', 'bill', 'error')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-billxyz', 'Missing BillXYZ'))
        try:
            bills_report(self.jur)
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Bill Importer needs update for new issue.')
        self.assertEqual(exception_raised, True)


class VoteEventReportTests(BaseReportTestCase):

    def setUp(self):
        super().setUp()
        ls = LegislativeSession.objects.create(jurisdiction=self.jur,
                                               identifier="2017",
                                               name="2017 Test Session",
                                               start_date="2017-06-25",
                                               end_date="2017-06-26")
        Person.objects.create(name="Voter")
        Bill.objects.create(legislative_session=ls, identifier="Bill for VoteEvent")

    def test_voteevent_missing_voters(self):
        org = Organization.objects.get(name="Democratic")
        bill = Bill.objects.get(identifier="Bill for VoteEvent")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects.create(
            identifier="vote1",
            motion_text="VoteEvent with missing-voters",
            start_date="2017-06-26",
            result='pass', legislative_session=ls,
            organization=org,
            bill=bill)

        # To check that on running twice no duplicate DataQualityIssue are being created.
        vote_events_report(self.jur)
        vote_events_report(self.jur)

        h = DataQualityIssue.objects.filter(object_id=voteevent.id,
                                            issue='voteevent-missing-voters').count()
        rest = DataQualityIssue.objects.exclude(object_id=voteevent.id,
                                                issue='voteevent-missing-voters')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_missing_bill(self):
        org = Organization.objects.get(name="Democratic")
        p = Person.objects.get(name="Voter")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects.create(identifier="vote1",
                                             motion_text="VoteEvent with missing-bill",
                                             start_date="2017-06-26",
                                             result='pass', legislative_session=ls,
                                             organization=org)
        voteevent.votes.create(option="yes", voter=p)
        voteevent.counts.create(option="yes", value=1)
        vote_events_report(self.jur)
        h = DataQualityIssue.objects.filter(object_id=voteevent.id,
                                            issue='voteevent-missing-bill').count()
        rest = DataQualityIssue.objects .exclude(object_id=voteevent.id,
                                                 issue='voteevent-missing-bill')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_unmatched_voter(self):
        org = Organization.objects.get(name="Democratic")
        bill = Bill.objects.get(identifier="Bill for VoteEvent")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects.create(identifier="vote1",
                                             motion_text="VoteEvent with unmatched-voter",
                                             start_date="2017-06-26",
                                             result='pass', legislative_session=ls,
                                             organization=org, bill=bill)
        voteevent.votes.create(option="yes", voter_name="unmatched-voter")
        voteevent.counts.create(option="yes", value=1)
        vote_events_report(self.jur)
        h = DataQualityIssue.objects.filter(object_id=voteevent.id,
                                            issue='voteevent-unmatched-voter').count()
        rest = DataQualityIssue.objects.exclude(object_id=voteevent.id,
                                                issue='voteevent-unmatched-voter')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_missing_counts(self):
        org = Organization.objects.get(name="Democratic")
        p = Person.objects.get(name="Voter")
        bill = Bill.objects.get(identifier="Bill for VoteEvent")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects.create(
            identifier="vote1",
            motion_text="VoteEvent with missing-counts",
            start_date="2017-06-26",
            result='pass', legislative_session=ls,
            organization=org,
            bill=bill)
        voteevent.votes.create(option="other", voter=p)
        voteevent.counts.create(option="other", value=1)
        voteevent.counts.create(option="yes", value=0)
        voteevent.counts.create(option="no", value=0)
        vote_events_report(self.jur)
        h = DataQualityIssue.objects.filter(object_id=voteevent.id,
                                            issue='voteevent-missing-counts').count()
        rest = DataQualityIssue.objects.exclude(object_id=voteevent.id,
                                                issue='voteevent-missing-counts')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_voteevent_bad_counts(self):
        org = Organization.objects.get(name="Democratic")
        p = Person.objects.get(name="Voter")
        bill = Bill.objects.get(identifier="Bill for VoteEvent")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects.create(
            identifier="vote1",
            motion_text="VoteEvent with bad-counts",
            start_date="2017-06-26",
            result='pass', legislative_session=ls,
            organization=org,
            bill=bill)
        voteevent.votes.create(option="yes", voter=p)
        voteevent.counts.create(option="yes", value=1)
        voteevent.counts.create(option="no", value=1)
        voteevent.counts.create(option="other", value=1)
        vote_events_report(self.jur)
        h = DataQualityIssue.objects.filter(object_id=voteevent.id,
                                            issue='voteevent-bad-counts').count()
        rest = DataQualityIssue.objects.exclude(object_id=voteevent.id,
                                                issue='voteevent-bad-counts')
        self.assertEqual(h, 1)
        self.assertQuerysetEqual(rest, [])

    def test_bill_delete_active_dqis(self):
        org = Organization.objects.get(name="Democratic")
        ls = LegislativeSession.objects.get(identifier="2017")
        voteevent = VoteEvent.objects.create(
            identifier="vote1",
            motion_text="VoteEvent with missing-bills & missingvoters",
            start_date="2017-06-26",
            result='pass', legislative_session=ls,
            organization=org)
        # Some Data Quality Issues
        DataQualityIssue.objects.create(jurisdiction=org.jurisdiction,
                                        content_object=voteevent,
                                        alert='error',
                                        issue='voteevent-missing-bill',
                                        status='ignored')
        DataQualityIssue.objects.create(jurisdiction=org.jurisdiction,
                                        content_object=voteevent,
                                        alert='warning',
                                        issue='voteevent-missing-voters',
                                        status='active')
        vote_events_report(self.jur)

        ignored_issues = DataQualityIssue.objects.filter(
            status='ignored', issue='voteevent-missing-bill')
        active_issues = DataQualityIssue.objects.filter(status='active')
        self.assertEqual(len(ignored_issues), 1)
        self.assertEqual(len(active_issues), 1)

    def test_voteevent_zzz_valueerror_on_not_updated_new_issue(self):
        IssueType('missing-votexyz', 'Missing VoteXYZ', 'voteevent', 'warning')
        DataQualityIssue._meta.get_field('issue').choices.append(
            ('missing-votexyz', 'Missing VoteXYZ'))
        try:
            vote_events_report(self.jur)
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'VoteEvents Importer needs update for new issue.')
        self.assertEqual(exception_raised, True)
