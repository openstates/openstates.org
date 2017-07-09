from opencivicdata.core.models import Person
from admintools.models import DataQualityIssue
from collections import defaultdict


def _prepare_import(issue_slug, post_data):
    if issue_slug == 'missing-photo':
        issue_items = dict((k, v) for k, v in post_data.items()
                           if v and not k.startswith('csrf'))
    elif issue_slug in ['missing-phone', 'missing-email', 'missing-address']:
        issue_items = defaultdict(dict)
        count = 1
        for k, v in post_data.items():
            if v and not k.startswith('csrf') and not k.startswith('note')  \
                    and not k.startswith('label'):
                c = k.split("ocd-person/")
                # using custom hash because two legislators can have same Phone
                # numbers for eg, `State House Message Phone`
                hash_ = str(count) + '__@#$__' + v
                issue_items[hash_]['id'] = "ocd-person/" + c[1]
                issue_items[hash_]['code'] = c[0]
                count += 1
        for hash_, item in issue_items.items():
            issue_items[hash_]['note'] = post_data['note_' + item['code']
                                                   + item['id']]
            issue_items[hash_]['label'] = post_data['label_' + item['code']
                                                    + item['id']]
    else:
        raise ValueError("Person Issue Resolver needs update for new issue.")
    return issue_items


def resolve_person_issues(issue_slug, post_data):
    issue_items = _prepare_import(issue_slug, post_data)
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
        objects_set = set()
        if issue_slug == 'missing-phone':
            type_ = 'voice'
        elif issue_slug in ['missing-email', 'missing-address']:
            type_ = issue_slug[8:]
        for hash_, items in issue_items.items():
            new_value = hash_.split('__@#$__')[1]
            p = Person.objects.get(id=items.get('id'))
            p.contact_details.create(type=type_, value=new_value,
                                     note=items.get('note'),
                                     label=items.get('label'))
            p.save()
            # not using .filter() directly to make sure that only one object is
            # being deleted from DataQualityIssue table.
            objects_set.add(p)
        for object_ in objects_set:
            dqi = DataQualityIssue.objects.get(object_id=object_.id,
                                               issue='person-{}'
                                               .format(issue_slug))
            dqi.delete()
    return len(issue_items)
