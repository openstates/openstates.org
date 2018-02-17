from opencivicdata.core.models import Jurisdiction, Person
from dataquality.models import DataQualityIssue, IssueResolverPatch


# apply approved patches and delete that DataQualityIssue from DB (if exists).
def apply_person_patches(patches, jur_name):
    count = 0
    image_duplicates = []
    name_duplicates = []
    for patch in patches:
        person = Person.objects.get(id=patch.object_id)
        if patch.category == 'image':
            # Number of approved pathces for 'image' for a person must be one.
            ap = patches.filter(object_id=person.id, category='image').count()
            if ap == 1:
                # make sure that patch is not applied before.
                if not person.image == patch.new_value:
                    person.image = patch.new_value
                    person.save()
                    count += 1
                    if patch.alert == 'warning':
                        dqi = DataQualityIssue.objects \
                            .filter(object_id=person.id,
                                    issue='person-missing-photo')
                        assert dqi.count() <= 1, "Not more than one Data" \
                            " Quality Issue must be deleted."
                        dqi.delete()
            else:
                if patch.object_id not in image_duplicates:
                    p = Person.objects.get(id=patch.object_id).name
                    print("{}: Found {} `approved` patches of `image` "
                          "for \"{}\". skipping..."
                          .format(jur_name, ap, p))
                image_duplicates.append(patch.object_id)
        elif patch.category == 'name':
            # Number of approved pathces for 'name' for a person must be one.
            ap = patches.filter(object_id=person.id, category='name').count()
            if ap == 1:
                # make sure that patch is not applied before.
                if not person.name == patch.new_value:
                    person.name = patch.new_value
                    person.save()
                    count += 1
            else:
                if patch.object_id not in name_duplicates:
                    p = Person.objects.get(id=patch.object_id).name
                    print("{}: Found {} `approved` patches of `name` "
                          "for \"{}\". skipping..."
                          .format(jur_name, ap, p))
                name_duplicates.append(patch.object_id)
        elif patch.category in ['voice', 'address', 'email']:
            # make sure that patch is not applied before.
            if not person.contact_details.filter(type=patch.category,
                                                 value=patch.new_value):
                person.contact_details \
                    .update_or_create(type=patch.category,
                                      value=patch.old_value,
                                      defaults={'value': patch.new_value,
                                                'note': patch.note})
                count += 1
            if patch.alert == 'warning':
                dqi = DataQualityIssue.objects \
                    .filter(object_id=person.id, issue='person-missing-{}'
                            .format('phone' if patch.category == 'voice'
                                    else patch.category))
                assert dqi.count() <= 1, "Not more than one Data Quality " \
                    "Issue must be deleted."
                dqi.delete()
        else:
            raise ValueError("Resolvers Needs Update For New Category!")
    return count


def setup_person_resolver():
    all_jurs = Jurisdiction.objects.order_by('name')
    for jur in all_jurs:
        patches = IssueResolverPatch.objects.filter(jurisdiction=jur,
                                                    status='approved')
        count = apply_person_patches(patches, jur.name)
        print("Applied {} New Person Patches For {}".format(count, jur.name))
