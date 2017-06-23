from django import template
from opencivicdata.legislative.models import LegislativeSession

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()


@register.assignment_tag
def legislative_session_list(request, jur_name):
    legislative_sessions = LegislativeSession.objects.filter(
        jurisdiction__name__exact=jur_name).values('name', 'identifier') \
        .order_by('-identifier')
    return legislative_sessions
