from django.shortcuts import render
from pupa.models import RunPlan
from opencivicdata.core.models import Jurisdiction
from admintools.models import (PeopleReport, OrganizationReport,
                               BillReport, VoteEventReport)


def overview(request):
    rows = []
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        reports = {}
        reports['name'] = jur.name
        reports['people'] = {'warning': PeopleReport.objects.get(jurisdiction=jur).warnings_count}
        reports['orgs'] = {'warning': OrganizationReport.objects.get(jurisdiction=jur).warnings_count,
                           'error': OrganizationReport.objects.get(jurisdiction=jur).no_memberships_count}
        reports['bills'] = {'warning': BillReport.objects.get(jurisdiction=jur).warnings_count,
                            'action_error': BillReport.objects.get(jurisdiction=jur).no_actions_count}
        reports['voteevents'] = {'warning': VoteEventReport.objects.get(jurisdiction=jur).warnings_count,
                                 'bill_error': VoteEventReport.objects.get(jurisdiction=jur).missing_bill_count,
                                 'counts_error': VoteEventReport.objects.get(jurisdiction=jur).missing_counts_count,}

        run = RunPlan.objects.filter(jurisdiction=jur).order_by('-end_time').first()
        reports['run'] = {'status': run.success,
                          'date': run.end_time.date()}
        rows.append(reports)

    return render(request, 'admintools/index.html', {'rows': rows})
