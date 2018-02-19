from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.http import QueryDict
from django.template import Template, Context
from pupa.models import RunPlan
from opencivicdata.core.models import (Jurisdiction, Person, Division,
                                       Organization, Membership)
from opencivicdata.legislative.models import (Bill, VoteEvent, BillSponsorship,
                                              LegislativeSession, PersonVote)
from dataquality.models import DataQualityIssue, IssueResolverPatch


class OverviewViewTests(TestCase):

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
                id="ocd-division/country:us/state:da",
                name="Dausa State Senate",
                url="http://www.senate.da.gov",
                division=division,
            )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur1, success=True,
                               start_time=start_time, end_time=end_time)
        start_time = end_time + timezone.timedelta(minutes=10)
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur2, success=True,
                               start_time=start_time, end_time=end_time)

    def test_view_response(self):
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)

    def test_run_status_count(self):
        """
        count = None (if only last run failed)
        count = 0 (if last run was successful)
        count = X (last X runs failed, where X > 1)
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=False,
                               start_time=start_time, end_time=end_time)

        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        for item in response.context['rows']:
            if item[0] == jur.id:
                run_count = item[1]['run'].get('count')
        self.assertEqual(run_count, None)

        start_time = end_time + timezone.timedelta(minutes=10)
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=True,
                               start_time=start_time, end_time=end_time)
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        for item in response.context['rows']:
            if item[0] == jur.id:
                run_count = item[1]['run'].get('count')
        self.assertEqual(run_count, 0)

        start_time = end_time + timezone.timedelta(minutes=10)
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=False,
                               start_time=start_time, end_time=end_time)
        start_time = end_time + timezone.timedelta(minutes=10)
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur, success=False,
                               start_time=start_time, end_time=end_time)

        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        for item in response.context['rows']:
            if item[0] == jur.id:
                run_count = item[1]['run'].get('count')
        self.assertEqual(run_count, 2)

    def test_total_rows_count_no_dataqissue(self):
        """
        Total number of rows must be equal to total number of
        jurisdictions when there are no Data Quality Issues present.
        """
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rows']), 2)

    def test_total_rows_count_partial_dataqissue(self):
        """
        Total number of rows must be equal to total number of
        jurisdictions when some of them have Data Quality Issues.
        """
        jur1 = Jurisdiction.objects.get(name="Missouri State Senate")
        person = Person.objects.create(name="Hitesh Garg")
        DataQualityIssue.objects.create(content_object=person,
                                        issue='missing-photo',
                                        jurisdiction=jur1,
                                        status='active')
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rows']), 2)

    def test_total_rows_count_all_dataqissue(self):
        """
        Total number of rows must be equal to total number of
        jurisdictions when all of them have Data Quality Issues.
        """
        jur1 = Jurisdiction.objects.get(name="Missouri State Senate")
        jur2 = Jurisdiction.objects.get(name="Dausa State Senate")
        person1 = Person.objects.create(name="Hitesh Garg")
        DataQualityIssue.objects.create(content_object=person1,
                                        issue='missing-photo',
                                        jurisdiction=jur1,
                                        status='active')
        person2 = Person.objects.create(name="Garg Hitesh")
        DataQualityIssue.objects.create(content_object=person2,
                                        issue='missing-photo',
                                        jurisdiction=jur2,
                                        status='active')
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rows']), 2)

    def test_overview_with_jurisdictions(self):
        """
        Check to make sure that the overview page has jurisdiction name
        displayed.
        """
        response = self.client.get(reverse('overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Missouri State Senate")


class JurisdictionintroViewTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur1 = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        Jurisdiction.objects.create(
                id="ocd-division/country:us/state:ds",
                name="Dausa State Senate",
                url="http://www.senate.ds.gov",
                division=division,
            )
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur1, success=True,
                               start_time=start_time, end_time=end_time)

        person1 = Person.objects.create(name="Hitesh Garg")
        # Data Quality Issue
        DataQualityIssue.objects.create(content_object=person1,
                                        issue='person-missing-photo',
                                        jurisdiction=jur1,
                                        status='active')
        # Data Quality Exception
        DataQualityIssue.objects.create(content_object=person1,
                                        issue='person-missing-phone',
                                        jurisdiction=jur1,
                                        status='ignored')

    def test_view_response(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)

    def test_mergetool_response(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        response = self.client.get(reverse('merge',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)

    def test_dataqualityissue_count(self):
        """
        If a particular issue exists for a `related_class` then it's count
        will be greater than zero otherwise count will be zero.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['cards']['person']['missing-photo']['count'], 1)
        # some other checks
        self.assertEqual(
            response.context['cards']
            .get('organization')['no-memberships']['count'], 0)
        self.assertEqual(
            response.context['cards']['bill']
            .get('unmatched-person-sponsor')['count'], 0)

    def test_dataqualityexception_count(self):
        """
        If a particular exception exists for a `related_class` then it's count
        will be greater than zero otherwise count will be zero.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['exceptions']['person']['missing-phone']['count'],
            1)
        # some other checks
        self.assertEqual(
            response.context['exceptions']
            .get('organization')['no-memberships']['count'], 0)
        self.assertEqual(
            response.context['exceptions']['bill']
            .get('unmatched-person-sponsor')['count'], 0)

    def test_context_values(self):
        """
        To check that important context values are present.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('exceptions' in response.context)
        self.assertTrue('cards' in response.context)
        self.assertTrue('jur_id' in response.context)

    def test_organization_list(self):
        """
        Two orgs with same classification should be counted as one.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        Organization.objects.create(jurisdiction=jur, name="Democratic",
                                    classification='executive')
        Organization.objects.create(jurisdiction=jur, name="Republican",
                                    classification='executive')
        orgs_list = Organization.objects.filter(
            jurisdiction=jur).values('classification').distinct()
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['orgs'],
                                 ["{'classification': 'executive'}"])
        self.assertEqual(len(orgs_list), 1)

    def test_voteevent_orgs_list(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(jurisdiction=jur, name="Democratic",
                                          classification='executive')
        ls = LegislativeSession.objects.create(
                                            jurisdiction=jur,
                                            identifier="2017",
                                            name="2017 Test Session",
                                            start_date="2017-06-25",
                                            end_date="2017-06-26")
        VoteEvent.objects.create(identifier="V1", organization=org,
                                 legislative_session=ls)
        voteevent_orgs_list = VoteEvent.objects.filter(
            legislative_session__jurisdiction=jur) \
            .values('organization__name').distinct()
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['voteevent_orgs'],
                                 ["{'organization__name': 'Democratic'}"])
        self.assertEqual(len(voteevent_orgs_list), 1)

    def test_bill_from_orgs_list(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(jurisdiction=jur, name="Democratic",
                                          classification='executive')
        ls = LegislativeSession.objects.create(
                                            jurisdiction=jur,
                                            identifier="2017",
                                            name="2017 Test Session",
                                            start_date="2017-06-25",
                                            end_date="2017-06-26")
        Bill.objects.create(legislative_session=ls, identifier="SB 1",
                            title="Test Bill", from_organization=org)
        bill_from_orgs_list = Bill.objects.filter(
            legislative_session__jurisdiction=jur) \
            .values('from_organization__name').distinct()
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['bill_orgs'],
                                 ["{'from_organization__name': 'Democratic'}"])
        self.assertEqual(len(bill_from_orgs_list), 1)

    def test_legislative_session_list(self):
        jur1 = Jurisdiction.objects.get(name="Missouri State Senate")
        jur2 = Jurisdiction.objects.get(name="Dausa State Senate")
        LegislativeSession.objects.create(jurisdiction=jur1,
                                          identifier="2017",
                                          name="2017 Test Session",
                                          start_date="2017-06-25",
                                          end_date="2017-06-26")
        LegislativeSession.objects.create(jurisdiction=jur1,
                                          identifier="2016",
                                          name="2016 Test Session",
                                          start_date="2016-06-25",
                                          end_date="2016-06-26")
        LegislativeSession.objects.create(jurisdiction=jur2,
                                          identifier="2015",
                                          name="2015 Test Session",
                                          start_date="2015-06-25",
                                          end_date="2015-06-26")
        out = Template(
            "{% load tags %}"
            "{% legislative_session_list jur_id as sessions %}"
            "{% for session in sessions %}"
            "{{ session.name }},"
            "{% endfor %}"
        ).render(Context({'jur_id': jur1.id}))
        self.assertIn('2017 Test Session', out)
        self.assertIn('2016 Test Session', out)
        self.assertNotIn('2015 Test Session', out)


class ListissueobjectsViewTests(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur1 = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(minutes=10)
        RunPlan.objects.create(jurisdiction=jur1, success=True,
                               start_time=start_time, end_time=end_time)

        LegislativeSession.objects.create(jurisdiction=jur1,
                                          identifier="2017",
                                          name="2017 Test Session",
                                          start_date="2017-06-25",
                                          end_date="2017-06-26")

    def test_important_context_values(self):
        """
        To check that important context values are present.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        person1 = Person.objects.create(name="Hitesh Garg")
        DataQualityIssue.objects.create(content_object=person1,
                                        issue='person-missing-photo',
                                        jurisdiction=jur,
                                        status='active')
        response = self.client.get(reverse('list_issue_objects',
                                           args=(jur.id,
                                                 'person',
                                                 'missing-photo')))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('objects' in response.context)
        self.assertTrue('url_slug' in response.context)
        self.assertTrue('jur_id' in response.context)

    def test_person_filter_queries(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        person1 = Person.objects.create(name="Hitesh Garg")
        DataQualityIssue.objects.create(content_object=person1,
                                        issue='person-missing-photo',
                                        jurisdiction=jur)
        query_dict = QueryDict('', mutable=True)
        # When Number of search results > 0
        query_dict.update({'person': "Hitesh"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'person', 'missing-photo')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'], 'core_person_change')
        self.assertEqual(response.context['issue_slug'], 'missing-photo')
        self.assertEqual(response.context['objects'].paginator.count, 1)

        # When Number of search results = 0
        query_dict.update({'person': "unknown person"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'person', 'missing-photo')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'], 'core_person_change')
        self.assertEqual(response.context['issue_slug'], 'missing-photo')
        self.assertEqual(response.context['objects'].paginator.count, 0)

    def test_organization_filter_queries(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="No Membership",
                                          classification="Test Organization",
                                          jurisdiction=jur)
        DataQualityIssue.objects.create(content_object=org,
                                        issue='organization-no-memberships',
                                        jurisdiction=jur)
        query_dict = QueryDict('', mutable=True)
        # When Number of search results > 0
        query_dict.update({'organization': "No",
                           'org_classification': "Test"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'organization',
                                           'no-memberships')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'],
                         'core_organization_change')
        self.assertEqual(response.context['issue_slug'],
                         'no-memberships')
        self.assertEqual(response.context['objects'].paginator.count, 1)

        # When Number of search results = 0
        query_dict.update({'organization': "unknown",
                           'org_classification': "unknown"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'organization',
                                           'no-memberships')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'],
                         'core_organization_change')
        self.assertEqual(response.context['issue_slug'],
                         'no-memberships')
        self.assertEqual(response.context['objects'].paginator.count, 0)

    def test_membership_filter_queries(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="Unmatched Person Memberships",
                                          jurisdiction=jur)
        mem = Membership.objects.create(person_name='Unmatched Person',
                                        organization=org)
        DataQualityIssue.objects.create(content_object=mem,
                                        issue='membership-unmatched-person',
                                        jurisdiction=jur)
        query_dict = QueryDict('', mutable=True)
        # When Number of search results > 0
        query_dict.update({'membership_org': "Unmatched Person Memberships",
                           'membership': "Unmatched Person"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'membership',
                                           'unmatched-person')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'], None)
        self.assertEqual(response.context['issue_slug'],
                         'unmatched-person')
        self.assertEqual(response.context['objects'].paginator.count, 1)

        # When Number of search results = 0
        query_dict.update({'membership_org': "unknown",
                           'membership': "unknown"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'membership',
                                           'unmatched-person')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'], None)
        self.assertEqual(response.context['issue_slug'],
                         'unmatched-person')
        self.assertEqual(response.context['objects'].paginator.count, 0)

    def test_bill_filter_queries(self):
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
        DataQualityIssue.objects.create(content_object=bill,
                                        issue='bill-unmatched-person-sponsor',
                                        jurisdiction=jur)
        query_dict = QueryDict('', mutable=True)
        # When Number of search results > 0
        query_dict.update({'bill_identifier': "Bill:",
                           "bill_session": "2017"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'bill',
                                           'unmatched-person-sponsor')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'],
                         'legislative_bill_change')
        self.assertEqual(response.context['issue_slug'],
                         'unmatched-person-sponsor')
        self.assertEqual(response.context['objects'].paginator.count, 1)

        # When Number of search results = 0
        query_dict.update({'bill_identifier': "unknown",
                           "bill_session": "unknown"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'bill',
                                           'unmatched-person-sponsor')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'],
                         'legislative_bill_change')
        self.assertEqual(response.context['issue_slug'],
                         'unmatched-person-sponsor')
        self.assertEqual(response.context['objects'].paginator.count, 0)

    def test_voteevent_filter_queries(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(name="Democratic", jurisdiction=jur)
        ls = LegislativeSession.objects.get(identifier="2017")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill for VoteEvent")
        voteevent = VoteEvent.objects \
            .create(identifier="vote1",
                    motion_text="VoteEvent with missing-voters",
                    start_date="2017-06-26",
                    result='pass', legislative_session=ls,
                    organization=org,
                    bill=bill)
        DataQualityIssue.objects.create(content_object=voteevent,
                                        issue='voteevent-missing-voters',
                                        jurisdiction=jur)
        query_dict = QueryDict('', mutable=True)
        # When Number of search results > 0
        query_dict.update({'voteevent_org': "Democratic",
                           'voteevent_bill': "Bill"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'voteevent',
                                           'missing-voters')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'],
                         'legislative_voteevent_change')
        self.assertEqual(response.context['issue_slug'],
                         'missing-voters')
        self.assertEqual(response.context['objects'].paginator.count, 1)

        # When Number of search results = 0
        query_dict.update({'voteevent_org': "unknown",
                           "voteevent_bill": "unknown"})
        url = '{base_url}?{querystring}' \
            .format(base_url=reverse('list_issue_objects',
                                     args=(jur.id, 'voteevent',
                                           'missing-voters')
                                     ),
                    querystring=query_dict.urlencode())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['url_slug'],
                         'legislative_voteevent_change')
        self.assertEqual(response.context['issue_slug'],
                         'missing-voters')
        self.assertEqual(response.context['objects'].paginator.count, 0)


class LegislativesessioninfoViewTest(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur1 = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        LegislativeSession.objects.create(jurisdiction=jur1,
                                          identifier="2017",
                                          name="2017 Test Session",
                                          start_date="2017-06-25",
                                          end_date="2017-06-26")
        LegislativeSession.objects.create(jurisdiction=jur1,
                                          identifier="2016",
                                          name="2016 Test Session",
                                          start_date="2016-06-25",
                                          end_date="2016-06-26")

    def test_view_response(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        ls = LegislativeSession.objects.get(identifier="2017",
                                            jurisdiction=jur)
        response = self.client.get(reverse('legislative_session_info',
                                           args=(jur.id, ls.identifier)))
        self.assertEqual(response.status_code, 200)

    def test_bill_from_orgs_list_if_exists(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(jurisdiction=jur,
                                          name="Democratic",
                                          classification='executive')
        ls = LegislativeSession.objects.get(identifier="2017",
                                            jurisdiction=jur)

        Bill.objects.create(legislative_session=ls, identifier="SB 1",
                            title="Test Bill", from_organization=org)
        bill_from_orgs_list = Bill.objects.filter(
            legislative_session__jurisdiction=jur,
            legislative_session__identifier=ls.identifier) \
            .values('from_organization__name').distinct()

        response = self.client.get(reverse('legislative_session_info',
                                           args=(jur.id,
                                                 ls.identifier)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['bill_orgs'],
            ["{'from_organization__name': 'Democratic'}"])
        self.assertEqual(len(bill_from_orgs_list), 1)

    def test_bill_from_orgs_list_if_not_exists(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(jurisdiction=jur,
                                          name="Democratic",
                                          classification='executive')
        ls = LegislativeSession.objects.get(identifier="2017",
                                            jurisdiction=jur)
        ls_2016 = LegislativeSession.objects.get(identifier="2016",
                                                 jurisdiction=jur)
        Bill.objects.create(legislative_session=ls, identifier="SB 1",
                            title="Test Bill", from_organization=org)
        bill_from_orgs_list = Bill.objects.filter(
            legislative_session__jurisdiction=jur,
            legislative_session__identifier=ls_2016.identifier) \
            .values('from_organization__name').distinct()

        response = self.client.get(reverse('legislative_session_info',
                                           args=(jur.id,
                                                 ls_2016.identifier)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['bill_orgs'], [])
        self.assertEqual(len(bill_from_orgs_list), 0)

    def test_voteevent_orgs_list_if_exists(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(jurisdiction=jur, name="Democratic",
                                          classification='executive')
        ls = LegislativeSession.objects.get(jurisdiction=jur,
                                            identifier="2017")
        VoteEvent.objects.create(identifier="V1", organization=org,
                                 legislative_session=ls)
        voteevent_orgs_list = VoteEvent.objects.filter(
            legislative_session__jurisdiction=jur) \
            .values('organization__name').distinct()
        response = self.client.get(reverse('legislative_session_info',
                                           args=(jur.id,
                                                 ls.identifier)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['voteevent_orgs'],
                                 ["{'organization__name': 'Democratic'}"])
        self.assertEqual(len(voteevent_orgs_list), 1)

    def test_voteevent_orgs_list_if_not_exists(self):
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        org = Organization.objects.create(jurisdiction=jur, name="Democratic",
                                          classification='executive')
        ls = LegislativeSession.objects.get(jurisdiction=jur,
                                            identifier="2017")
        ls_2016 = LegislativeSession.objects.get(identifier="2016",
                                                 jurisdiction=jur)
        VoteEvent.objects.create(identifier="V1", organization=org,
                                 legislative_session=ls)
        voteevent_orgs_list = VoteEvent.objects.filter(
            legislative_session__jurisdiction=jur,
            legislative_session__identifier=ls_2016.identifier) \
            .values('organization__name').distinct()
        response = self.client.get(reverse('legislative_session_info',
                                           args=(jur.id,
                                                 ls_2016.identifier)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['voteevent_orgs'], [])
        self.assertEqual(len(voteevent_orgs_list), 0)


class RetireLegislatorsViewTest(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        person = Person.objects.create(name="Hitesh Garg")
        org1 = Organization.objects.create(name="Democratic", jurisdiction=jur)
        org2 = Organization.objects.create(name="Republican", jurisdiction=jur)
        org3 = Organization.objects.create(name="House", jurisdiction=jur)
        org4 = Organization.objects.create(name="Senate", jurisdiction=jur)
        org5 = Organization.objects.create(name="Joint", jurisdiction=jur)
        Membership.objects.create(person=person, organization=org1,
                                  end_date='2017-12-25')
        Membership.objects.create(person=person, organization=org2,
                                  end_date='2017-12-23')
        Membership.objects.create(person=person, organization=org3)
        Membership.objects.create(person=person, organization=org4)
        Membership.objects.create(person=person, organization=org5)

    def test_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('retire_legislators',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        person = Person.objects.get(name="Hitesh Garg")
        self.assertTrue(person in response.context['people'].object_list)

    def test_wrong_format_of_reitrement_date(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        p = Person.objects.get(name="Hitesh Garg")
        # Suppose retirement_date == '2017-12-24' (This is not possible)
        url = reverse('retire_legislators', args=(jur.id,))
        data = {p.id: '2017-12-35'}
        response = self.client.post(url, data)
        # some basic checks
        self.assertTrue('jur_id' in response.context)
        self.assertTrue('people' in response.context)
        self.assertTrue('page_range' in response.context)
        # Memberships should not be updated
        mem = Membership.objects.filter(person=p, end_date='2017-12-35')
        self.assertQuerysetEqual(mem, [])

    def test_invalid_retirement_date(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        p = Person.objects.get(name="Hitesh Garg")
        # Suppose retirement_date == '2017-12-24' (This is not possible)
        url = reverse('retire_legislators', args=(jur.id,))
        data = {p.id: '2017-12-24'}
        response = self.client.post(url, data)
        # some basic checks
        self.assertTrue('jur_id' in response.context)
        self.assertTrue('people' in response.context)
        self.assertTrue('page_range' in response.context)
        # Memberships should not be updated
        mem = Membership.objects.filter(person=p, end_date='2017-12-24')
        self.assertQuerysetEqual(mem, [])

    def test_valid_retirement_date(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        p = Person.objects.get(name="Hitesh Garg")
        org1 = Organization.objects.get(name="Democratic")
        # Suppose retirement_date == '2017-12-30'
        url = reverse('retire_legislators', args=(jur.id,))
        data = {p.id: '2017-12-30'}
        self.client.post(url, data)
        m1 = Membership.objects.get(organization=org1)
        self.assertEqual(m1.end_date, '2017-12-25')
        mem = Membership.objects.filter(person=p,
                                        end_date='2017-12-30').count()
        self.assertEqual(mem, 3)


class ListRetiredLegislatorsViewTest(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        person = Person.objects.create(name="Hitesh Garg")
        org1 = Organization.objects.create(name="Democratic", jurisdiction=jur)
        org2 = Organization.objects.create(name="Republican", jurisdiction=jur)
        org3 = Organization.objects.create(name="House", jurisdiction=jur)
        org4 = Organization.objects.create(name="Senate", jurisdiction=jur)
        org5 = Organization.objects.create(name="Joint", jurisdiction=jur)
        # Suppose retirement_date == '2017-12-30'
        Membership.objects.create(person=person, organization=org1,
                                  end_date='2017-12-25')
        Membership.objects.create(person=person, organization=org2,
                                  end_date='2017-12-30')
        Membership.objects.create(person=person, organization=org3,
                                  end_date='2017-12-30')
        Membership.objects.create(person=person, organization=org4,
                                  end_date='2017-12-30')
        Membership.objects.create(person=person, organization=org5,
                                  end_date='2017-12-30')

    def test_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        person = Person.objects.get(name="Hitesh Garg")
        response = self.client.get(reverse('list_retired_legislators',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['people'].object_list[0][0],
                         person)
        self.assertEqual(response.context['people'].object_list[0][1],
                         '2017-12-30')

    def test_valid_update_in_retirement_date(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        p = Person.objects.get(name="Hitesh Garg")
        org1 = Organization.objects.get(name="Democratic")
        url = reverse('list_retired_legislators', args=(jur.id,))
        data = {p.id: '2017-12-26'}
        self.client.post(url, data)
        m1 = Membership.objects.get(organization=org1)
        self.assertEqual(m1.end_date, '2017-12-25')
        mem = Membership.objects.filter(person=p,
                                        end_date='2017-12-26').count()
        self.assertEqual(mem, 4)

    def test_wrong_format_of_update_in_retirement_date(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        p = Person.objects.get(name="Hitesh Garg")
        org1 = Organization.objects.get(name="Democratic")
        url = reverse('list_retired_legislators', args=(jur.id,))
        data = {p.id: '2017-12-56'}
        self.client.post(url, data)
        m1 = Membership.objects.get(organization=org1)
        self.assertEqual(m1.end_date, '2017-12-25')
        mem = Membership.objects.filter(person=p,
                                        end_date='2017-12-56').count()
        self.assertEqual(mem, 0)
        mem = Membership.objects.filter(person=p,
                                        end_date='2017-12-30').count()
        self.assertEqual(mem, 4)

    def test_invalid_update_in_retirement_date(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        p = Person.objects.get(name="Hitesh Garg")
        org1 = Organization.objects.get(name="Democratic")
        url = reverse('list_retired_legislators', args=(jur.id,))
        data = {p.id: '2017-12-24'}
        self.client.post(url, data)
        m1 = Membership.objects.get(organization=org1)
        self.assertEqual(m1.end_date, '2017-12-25')
        mem = Membership.objects.filter(person=p,
                                        end_date='2017-12-24').count()
        self.assertEqual(mem, 0)
        mem = Membership.objects.filter(person=p,
                                        end_date='2017-12-30').count()
        self.assertEqual(mem, 4)

    def test_un_retire_a_legislator(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        p = Person.objects.get(name="Hitesh Garg")
        org1 = Organization.objects.get(name="Democratic")
        url = reverse('list_retired_legislators', args=(jur.id,))
        data = {p.id: ''}
        self.client.post(url, data)
        m1 = Membership.objects.get(organization=org1)
        self.assertEqual(m1.end_date, '2017-12-25')
        mem = Membership.objects.filter(person=p, end_date='').count()
        self.assertEqual(mem, 4)


class CreatePersonPatchViewTest(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        person1 = Person.objects.create(name="Hitesh Garg")
        person2 = Person.objects.create(name="sheenu")
        org = Organization.objects.create(name="Democratic", jurisdiction=jur)
        Membership.objects.create(person=person1, organization=org)
        Membership.objects.create(person=person2, organization=org)

    def test_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('create_person_patch',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('jur_id' in response.context)
        self.assertTrue('people' in response.context)

    def test_create_a_patch(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('create_person_patch',
                                           args=(jur.id,)))
        p1 = Person.objects.get(name="Hitesh Garg")
        p2 = Person.objects.get(name="sheenu")
        self.assertTrue(p1 in response.context['people'])
        self.assertTrue(p2 in response.context['people'])
        # Let's create a patch for person1
        data = {'person': p1.id,
                'old_value': 'Hitesh Garg',
                'new_value': 'Garg Hitesh',
                'category': 'name',
                'note': 'some note',
                'source': None}
        url = reverse('create_person_patch', args=(jur.id,))
        response = self.client.post(url, data)
        person1 = Person.objects.get(id=p1.id)
        patch = IssueResolverPatch.objects.get(object_id=p1.id,
                                               status='unreviewed')
        self.assertEqual(patch.new_value, 'Garg Hitesh')
        self.assertEqual(person1.name, "Hitesh Garg")


class NameResolutionToolViewTest(TestCase):

    def setUp(self):
        division = Division.objects.create(
            id='ocd-division/country:us', name='USA')
        jur = Jurisdiction.objects.create(
                id="ocd-division/country:us/state:mo",
                name="Missouri State Senate",
                url="http://www.senate.mo.gov",
                division=division,
            )
        Person.objects.create(name="Hitesh Garg")
        Person.objects.create(name="sheenu")
        org = Organization.objects.create(name="Democratic", jurisdiction=jur)
        Membership.objects.create(person_name="Unmatched Name1",
                                  organization=org)
        Membership.objects.create(person_name="Unmatched Name2",
                                  organization=org)
        ls = LegislativeSession.objects.create(jurisdiction=jur,
                                               identifier="2017",
                                               name="2017 Test Session",
                                               start_date="2017-06-25",
                                               end_date="2017-06-26")
        bill = Bill.objects.create(legislative_session=ls,
                                   identifier="Bill with Unmatched Sponsors")
        BillSponsorship.objects.create(bill=bill, entity_type='person',
                                       name='Unmatched Sponsor 1')
        BillSponsorship.objects.create(bill=bill, entity_type='person',
                                       name='Unmatched Sponsor 2')
        voteevent = VoteEvent.objects \
            .create(identifier="vote1",
                    motion_text="VoteEvent with missing-voters",
                    start_date="2017-06-26",
                    result='pass', legislative_session=ls,
                    organization=org,
                    bill=bill)
        PersonVote.objects.create(vote_event=voteevent,
                                  voter_name='Unmatched Voter 1')
        PersonVote.objects.create(vote_event=voteevent,
                                  voter_name='Unmatched Voter 2')

    def test_unmatched_memberships_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('name_resolution_tool',
                                           args=(jur.id,
                                                 'unmatched_memberships')))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('jur_id' in response.context)
        self.assertTrue('page_range' in response.context)
        self.assertTrue('people' in response.context)
        self.assertTrue('unresolved' in response.context)
        self.assertEqual(response.context['category'], 'unmatched_memberships')
        d = dict(response.context['unresolved'].object_list)
        mem1 = Membership.objects.get(person_name="Unmatched Name1")
        mem2 = Membership.objects.get(person_name="Unmatched Name2")
        self.assertEqual(d[mem1.person_name], 1)
        self.assertEqual(d[mem2.person_name], 1)

    def test_unmatched_voteevent_voters_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('name_resolution_tool',
                                           args=(jur.id,
                                                 'unmatched_voteevent_voters')
                                           ))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('jur_id' in response.context)
        self.assertTrue('page_range' in response.context)
        self.assertTrue('people' in response.context)
        self.assertTrue('unresolved' in response.context)
        self.assertEqual(response.context['category'],
                         'unmatched_voteevent_voters')
        d = dict(response.context['unresolved'].object_list)
        v1 = PersonVote.objects.get(voter_name="Unmatched Voter 1")
        v2 = PersonVote.objects.get(voter_name="Unmatched Voter 2")
        self.assertEqual(d[v1.voter_name], 1)
        self.assertEqual(d[v2.voter_name], 1)

    def test_unamtched_bill_sponsors_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('name_resolution_tool',
                                           args=(jur.id,
                                                 'unmatched_bill_sponsors')))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('jur_id' in response.context)
        self.assertTrue('page_range' in response.context)
        self.assertTrue('people' in response.context)
        self.assertTrue('unresolved' in response.context)
        self.assertEqual(response.context['category'],
                         'unmatched_bill_sponsors')
        d = dict(response.context['unresolved'].object_list)
        sp1 = BillSponsorship.objects.get(name='Unmatched Sponsor 1')
        sp2 = BillSponsorship.objects.get(name='Unmatched Sponsor 2')
        self.assertEqual(d[sp1.name], 1)
        self.assertEqual(d[sp2.name], 1)

    def test_unknown_category_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        try:
            self.client.get(reverse('name_resolution_tool',
                                    args=(jur.id, 'unknown_category')))
        except ValueError as e:
            exception_raised = True
            self.assertEqual(str(e), 'Name Resolution Tool needs update for '
                             'new category')
        self.assertEqual(exception_raised, True)

    def test_matching_unmatched_memberships(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        mem1 = Membership.objects.get(person_name="Unmatched Name1")
        mem2 = Membership.objects.get(person_name="Unmatched Name2")
        p1 = Person.objects.get(name="Hitesh Garg")
        p2 = Person.objects.get(name="sheenu")
        data = {
            mem1.person_name: p1.id,
            mem2.person_name: p2.id
        }
        url = reverse('name_resolution_tool',
                      args=(jur.id, 'unmatched_memberships'))
        self.assertEqual(mem1.person, None)
        self.assertEqual(mem2.person, None)
        response = self.client.post(url, data)
        self.assertEqual(len(response.context['unresolved'].object_list), 0)
        # getting Updated objects
        mem1 = Membership.objects.get(id=mem1.id)
        mem2 = Membership.objects.get(id=mem2.id)
        self.assertEqual(mem1.person.id, p1.id)
        self.assertEqual(mem2.person.id, p2.id)

    def test_matching_unmatched_voteevent_voters(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        pv1 = PersonVote.objects.get(voter_name="Unmatched Voter 1")
        pv2 = PersonVote.objects.get(voter_name="Unmatched Voter 2")
        p1 = Person.objects.get(name="Hitesh Garg")
        p2 = Person.objects.get(name="sheenu")
        data = {
            pv1.voter_name: p1.id,
            pv2.voter_name: p2.id
        }
        url = reverse('name_resolution_tool',
                      args=(jur.id, 'unmatched_voteevent_voters'))
        self.assertEqual(pv1.voter, None)
        self.assertEqual(pv2.voter, None)
        response = self.client.post(url, data)
        self.assertEqual(len(response.context['unresolved'].object_list), 0)
        # getting Updated objects
        pv1 = PersonVote.objects.get(id=pv1.id)
        pv2 = PersonVote.objects.get(id=pv2.id)
        self.assertEqual(pv1.voter_id, p1.id)
        self.assertEqual(pv2.voter_id, p2.id)

    def test_matching_unmatched_bill_sponsors(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        sp1 = BillSponsorship.objects.get(name='Unmatched Sponsor 1')
        sp2 = BillSponsorship.objects.get(name='Unmatched Sponsor 2')
        p1 = Person.objects.get(name="Hitesh Garg")
        p2 = Person.objects.get(name="sheenu")
        data = {
            sp1.name: p1.id,
            sp2.name: p2.id
        }
        url = reverse('name_resolution_tool',
                      args=(jur.id, 'unmatched_bill_sponsors'))
        self.assertEqual(sp1.person, None)
        self.assertEqual(sp2.person, None)
        response = self.client.post(url, data)
        self.assertEqual(len(response.context['unresolved'].object_list), 0)
        # getting Updated objects
        sp1 = BillSponsorship.objects.get(id=sp1.id)
        sp2 = BillSponsorship.objects.get(id=sp2.id)
        self.assertEqual(sp1.person_id, p1.id)
        self.assertEqual(sp2.person_id, p2.id)


class ReviewPatchesViewTest(TestCase):

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
        org = Organization.objects.create(name="Democratic", jurisdiction=jur)
        Membership.objects.create(person=p, organization=org)
        # some `unreviewed` patches.
        IssueResolverPatch.objects.create(content_object=p,
                                          jurisdiction=jur,
                                          status='unreviewed',
                                          old_value='Hitesh Garg',
                                          new_value='Garg',
                                          category='name',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=p,
                                          jurisdiction=jur,
                                          status='rejected',
                                          old_value='Hitesh Garg',
                                          new_value='Ga',
                                          category='name',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=p,
                                          jurisdiction=jur,
                                          status='unreviewed',
                                          new_value='http://www/image.png',
                                          category='image',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=p,
                                          jurisdiction=jur,
                                          status='deprecated',
                                          new_value='http://www/right.png',
                                          category='image',
                                          applied_by='user')

    def test_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('review_person_patches',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('jur_id' in response.context)
        self.assertTrue('patches' in response.context)

    def test_only_unreviewed_pathces_are_coming_up(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('review_person_patches',
                                           args=(jur.id,)))
        unreviewed_patches = IssueResolverPatch.objects \
            .filter(jurisdiction=jur, status='unreviewed').count()
        self.assertEqual(len(response.context['patches'].object_list),
                         unreviewed_patches)

    def test_status_after_review(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        url = reverse('review_person_patches', args=(jur.id,))
        # there are 2 unreviewed patches
        patch1 = IssueResolverPatch.objects.get(new_value='Garg')
        patch2 = IssueResolverPatch.objects.get(
            new_value="http://www/image.png")
        data = {
            'name__{}__{}'.format(patch1.id, patch1.object_id): 'rejected',
            'image__{}__{}'.format(patch2.id, patch1.object_id): 'approved'

        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        # getting updated objects
        patch1 = IssueResolverPatch.objects.get(new_value='Garg')
        patch2 = IssueResolverPatch.objects.get(
            new_value="http://www/image.png")
        self.assertEqual(patch1.status, 'rejected')
        self.assertEqual(patch2.status, 'approved')
        self.assertQuerysetEqual(IssueResolverPatch.objects.filter(
            status='unreviewed'), [])


class ListAllPersonPatchesViewTest(TestCase):

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
        org = Organization.objects.create(name="Democratic", jurisdiction=jur)
        Membership.objects.create(person=p, organization=org)
        IssueResolverPatch.objects.create(content_object=p,
                                          jurisdiction=jur,
                                          status='unreviewed',
                                          old_value='Hitesh Garg',
                                          new_value='Garg',
                                          category='name',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=p,
                                          jurisdiction=jur,
                                          status='rejected',
                                          old_value='Hitesh Garg',
                                          new_value='Ga',
                                          category='name',
                                          applied_by='admin')
        IssueResolverPatch.objects.create(content_object=p,
                                          jurisdiction=jur,
                                          status='approved',
                                          new_value='http://www/image.png',
                                          category='image',
                                          applied_by='user')
        IssueResolverPatch.objects.create(content_object=p,
                                          jurisdiction=jur,
                                          status='deprecated',
                                          new_value='http://www/right.png',
                                          category='image',
                                          applied_by='user')

    def test_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('list_all_person_patches',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('jur_id' in response.context)
        self.assertTrue('patches' in response.context)

    def test_all_patches_are_coming_up(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('list_all_person_patches',
                                           args=(jur.id,)))
        self.assertEqual(len(response.context['patches'].object_list), 4)

    def test_modify_patch_status(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        patch = IssueResolverPatch.objects.get(new_value='Garg')
        self.assertEqual(patch.status, 'unreviewed')
        url = reverse('list_all_person_patches', args=(jur.id,))
        data = {patch.id: 'approved'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        # getting updated object
        patch = IssueResolverPatch.objects.get(new_value='Garg')
        self.assertEqual(patch.status, 'approved')

    def test_modified_multiple_approved_patch_for_image_or_name(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        patch = IssueResolverPatch.objects.get(
            new_value='http://www/right.png')
        self.assertEqual(patch.status, 'deprecated')
        url = reverse('list_all_person_patches', args=(jur.id,))
        data = {patch.id: 'approved'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        # getting updated object
        patch = IssueResolverPatch.objects.get(
            new_value='http://www/right.png')
        self.assertEqual(patch.status, 'deprecated')


class PersonResolveIssueViewTest(TestCase):

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
        p2 = Person.objects.create(name="Sheenu")
        org = Organization.objects.create(name="Democratic", jurisdiction=jur)
        Membership.objects.create(person=p, organization=org)
        Membership.objects.create(person=p2, organization=org)

    def test_create_missing_image_patch(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        url = reverse('person_resolve_issues', args=(jur.id, 'missing-photo'))
        p = Person.objects.get(name="Hitesh Garg")
        data = {p.id: 'http://www.image.png'}
        response = self.client.post(url, data)
        # HttpResponseRedirect (Found 302)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(IssueResolverPatch.objects.count(), 1)
        self.assertEqual(IssueResolverPatch.objects.filter(
            status='unreviewed').count(), 1)
        self.assertEqual(IssueResolverPatch.objects.filter(
            object_id=p.id).count(), 1)

    def test_create_missing_voice_patch(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        url = reverse('person_resolve_issues', args=(jur.id, 'missing-phone'))
        p = Person.objects.get(name="Hitesh Garg")
        data = {
            p.id: '102-658-894',
            'note_{}'.format(p.id): 'Capitol Office',
            '1_{}'.format(p.id): '258-965-624',
            'note_1_{}'.format(p.id): 'District Office'
        }
        response = self.client.post(url, data)
        # HttpResponseRedirect (Found 302)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(IssueResolverPatch.objects.count(), 2)
        patch = IssueResolverPatch.objects.get(new_value='102-658-894')
        self.assertEqual(patch.status, 'unreviewed')
        self.assertEqual(patch.category, 'voice')
        self.assertEqual(patch.note, 'Capitol Office')
        patch = IssueResolverPatch.objects.get(new_value='258-965-624')
        self.assertEqual(patch.status, 'unreviewed')
        self.assertEqual(patch.category, 'voice')
        self.assertEqual(patch.note, 'District Office')

    def test_create_missing_email_patch(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        url = reverse('person_resolve_issues', args=(jur.id, 'missing-email'))
        p = Person.objects.get(name="Hitesh Garg")
        p2 = Person.objects.get(name="Sheenu")
        data = {
            p.id: 'test@gmail.com',
            'note_{}'.format(p.id): 'Capitol Office',
            '1_{}'.format(p.id): 'right@gmail.com',
            'note_1_{}'.format(p.id): 'District Office',
            p2.id: 'person2@gmail.com',
            'note_{}'.format(p2.id): 'Person2 Office'
        }
        response = self.client.post(url, data)
        # HttpResponseRedirect (Found 302)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(IssueResolverPatch.objects.count(), 3)
        patch = IssueResolverPatch.objects.get(new_value='test@gmail.com')
        self.assertEqual(patch.status, 'unreviewed')
        self.assertEqual(patch.category, 'email')
        self.assertEqual(patch.note, 'Capitol Office')
        patch = IssueResolverPatch.objects.get(
            new_value='person2@gmail.com')
        self.assertEqual(patch.status, 'unreviewed')
        self.assertEqual(patch.category, 'email')
        self.assertEqual(patch.note, 'Person2 Office')
        patch = IssueResolverPatch.objects.get(new_value='right@gmail.com')
        self.assertEqual(patch.status, 'unreviewed')
        self.assertEqual(patch.category, 'email')
        self.assertEqual(patch.note, 'District Office')

    def test_create_missing_address_patch(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        url = reverse('person_resolve_issues', args=(jur.id,
                                                     'missing-address'))
        p = Person.objects.get(name="Hitesh Garg")
        data = {
            p.id: 'New York',
            'note_{}'.format(p.id): 'Capitol Office',
            '1_{}'.format(p.id): 'Maine',
            'note_1_{}'.format(p.id): 'District Office'
        }
        response = self.client.post(url, data)
        # HttpResponseRedirect (Found 302)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(IssueResolverPatch.objects.count(), 2)
        patch = IssueResolverPatch.objects.get(new_value='New York')
        self.assertEqual(patch.status, 'unreviewed')
        self.assertEqual(patch.category, 'address')
        self.assertEqual(patch.note, 'Capitol Office')
        patch = IssueResolverPatch.objects.get(new_value='Maine')
        self.assertEqual(patch.status, 'unreviewed')
        self.assertEqual(patch.category, 'address')
        self.assertEqual(patch.note, 'District Office')


class DataQualityExceptionsViewTest(TestCase):

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

    def test_view_response(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        response = self.client.get(reverse('dataquality_exceptions',
                                           args=(jur.id, 'missing-photo',
                                                 'remove')))
        self.assertEqual(response.status_code, 200)

    def test_listing_all_exceptions(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        org = Organization.objects.get(name="Democratic")
        p1 = Person.objects.create(name="John Snow")
        Membership.objects.create(person=p1, organization=org)
        p2 = Person.objects.create(name="Peter")
        Membership.objects.create(person=p2, organization=org)
        # some data quality exceptions
        DataQualityIssue.objects.create(jurisdiction=jur,
                                        content_object=p1,
                                        issue='person-missing-address',
                                        status='ignored',
                                        message='missing on remote site')
        DataQualityIssue.objects.create(jurisdiction=jur,
                                        content_object=p2,
                                        issue='person-missing-address',
                                        status='ignored',
                                        message='missing on openstates.org')
        response = self.client.get(reverse('dataquality_exceptions',
                                           args=(jur.id, 'missing-address',
                                                 'remove')))
        self.assertEqual(response.context['url_slug'], 'core_person_change')
        dqe = DataQualityIssue.objects.filter(status='ignored').count()
        self.assertEqual(len(response.context['objects'].object_list), dqe)

    def test_add_data_quality_exception(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        org = Organization.objects.get(name="Democratic")
        p1 = Person.objects.create(name="John Snow")
        Membership.objects.create(person=p1, organization=org)
        DataQualityIssue.objects.create(jurisdiction=jur,
                                        content_object=p1,
                                        issue='person-missing-address',
                                        status='active')
        data = {'message': 'remote site don\'t have address',
                p1.id: 'on'}
        url = reverse('dataquality_exceptions', args=(jur.id,
                                                      'missing-address',
                                                      'add'))
        self.client.post(url, data)
        dqe = DataQualityIssue.objects.get(object_id=p1.id)
        self.assertEqual(dqe.status, 'ignored')
        self.assertEqual(dqe.message, 'remote site don\'t have address')
        self.assertQuerysetEqual(DataQualityIssue.objects.filter(
            status='active'), [])

    def test_remove_data_quality_exception(self):
        jur = Jurisdiction.objects.get(id='ocd-division/country:us/state:mo')
        org = Organization.objects.get(name="Democratic")
        p1 = Person.objects.create(name="John Snow")
        Membership.objects.create(person=p1, organization=org)
        DataQualityIssue.objects.create(jurisdiction=jur,
                                        content_object=p1,
                                        issue='person-missing-address',
                                        status='ignored',
                                        message='error on website')
        url = reverse('dataquality_exceptions', args=(jur.id,
                                                      'missing-address',
                                                      'remove'))
        data = {'error on website__@#$__{}'.format(p1.id): 'on'}
        self.client.post(url, data)
        dqe = DataQualityIssue.objects.get(object_id=p1.id)
        self.assertEqual(dqe.status, 'active')
        self.assertEqual(dqe.message, '')
        self.assertQuerysetEqual(DataQualityIssue.objects.filter(
            status='ignored'), [])
