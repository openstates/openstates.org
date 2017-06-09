from django.shortcuts import render
from pupa.models import RunPlan
from opencivicdata.core.models import Jurisdiction
from admintools.models import PeopleReport, OrganizationReport


def overview(request):
    rows = []
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        reports = {}
        reports['name'] = jur.name
        reports['people'] = {'warning': PeopleReport.objects.get(jurisdiction=jur).warnings_count}
        reports['orgs'] = {'warning': OrganizationReport.objects.get(jurisdiction=jur).warnings_count,
                           'error': OrganizationReport.objects.get(jurisdiction=jur).errors_count}
        run = RunPlan.objects.filter(jurisdiction=jur) \
            .order_by('-end_time').first()
        reports['run'] = {'status': run.success,
                          'date': run.end_time.date()}
        rows.append(reports)

    return render(request, 'admintools/index.html', {'rows': rows})
