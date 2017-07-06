from opencivicdata.core.models import Person
from admintools.models import DataQualityIssue


def resolve_person_issues(issue_slug, issue_items):
    if issue_slug == 'missing-photo':
        for identifier, value in issue_items.items():
            p = Person.objects.get(id=identifier)
            p.image = value
            p.save()
            dqi = DataQualityIssue.objects \
                .get(object_id=identifier,
                     issue='person-missing-photo')
            dqi.delete()
    else:
        if issue_slug == 'missing-phone':
            type_ = 'voice'
        else:
            type_ = issue_slug[8:]
        for identifier, values in issue_items.items():
            p = Person.objects.get(id=identifier)
            p.contact_details.create(type=type_, value=values.get('value'),
                                     note=values.get('note'),
                                     label=values.get('label'))
            dqi = DataQualityIssue.objects.get(object_id=identifier,
                                               issue='person-{}'
                                               .format(issue_slug))
            dqi.delete()
