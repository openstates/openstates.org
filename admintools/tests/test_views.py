from django.test import TestCase
from pupa.models import RunPlan
from opencivicdata.core.models import (Jurisdiction, Person, Division,
                                       Organization, Membership)
from opencivicdata.legislative.models import (Bill, VoteEvent,
                                              LegislativeSession)
from django.utils import timezone
from admintools.models import DataQualityIssue
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.template import Template, Context


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
                                        alert='warning',
                                        jurisdiction=jur1)
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
                                        alert='warning',
                                        jurisdiction=jur1)
        person2 = Person.objects.create(name="Garg Hitesh")
        DataQualityIssue.objects.create(content_object=person2,
                                        issue='missing-photo',
                                        alert='warning',
                                        jurisdiction=jur2)
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
        DataQualityIssue.objects.create(content_object=person1,
                                        issue='person-missing-photo',
                                        alert='warning',
                                        jurisdiction=jur1)

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

    def test_context_values(self):
        """
        To check that important context values are present.
        """
        jur = Jurisdiction.objects.get(name="Missouri State Senate")
        response = self.client.get(reverse('jurisdiction_intro',
                                           args=(jur.id,)))
        self.assertEqual(response.status_code, 200)
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
                                        alert='warning',
                                        jurisdiction=jur)
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
                                        alert='warning',
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
                                        alert='error',
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
                                        alert='warning',
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
                                        alert='warning',
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
                                        alert='error',
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
