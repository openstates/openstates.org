from opencivicdata.core.models import Person
from dataquality.models import DataQualityIssue, IssueResolverPatch


# apply approved patches and create new issues, in case a scraper scrapes a new value
# which doesn't match with old_value of patch(which can be ignored later if scraping was correct)
def apply_person_patches(jur_name):
    count = 0
    patches = IssueResolverPatch.objects.filter(jurisdiction__name=jur_name,
                                                status='approved')
    image_duplicates = []
    name_duplicates = []
    for patch in patches:
        person = Person.objects.get(id=patch.object_id)
        issue = None
        if patch.category == 'image':
            # Number of approved pathces for 'image' for a person must be one.
            ap = patches.filter(object_id=person.id, category='image').count()
            if ap == 1:
                if person.image == patch.old_value:
                    # make sure that patch is not applied before.
                    if not person.image == patch.new_value:
                        person.image = patch.new_value
                        person.save()
                        count += 1
                else:
                    if patch.old_value:
                        issue = 'wrong-photo'
                    else:
                        issue = 'person-missing-photo'

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
                if person.name == patch.old_value:
                    # make sure that patch is not applied before.
                    if not person.name == patch.new_value:
                        person.name = patch.new_value
                        person.save()
                        count += 1
                else:
                    issue = 'wrong-name'
            else:
                if patch.object_id not in name_duplicates:
                    p = Person.objects.get(id=patch.object_id).name
                    print("{}: Found {} `approved` patches of `name` "
                          "for \"{}\". skipping..."
                          .format(jur_name, ap, p))
                name_duplicates.append(patch.object_id)
        elif patch.category in ['voice', 'address', 'email']:
            contact = person.contact_details.filter(type=patch.category,
                                                    value=patch.old_value)
            if contact:
                if not person.contact_details.filter(type=patch.category,
                                                     value=patch.new_value):
                    contact.update(value=patch.new_value)
                    count += 1
            elif patch.old_value == '':
                if not person.contact_details.filter(type=patch.category,
                                                     value=patch.new_value):
                    person.contact_details.create(type=patch.category,
                                                  value=patch.new_value)
                    count += 1
            else:
                if patch.category == 'voice':
                    issue = 'wrong-phone'
                elif patch.category == 'address':
                    issue = 'wrong-address'
                elif patch.category == 'email':
                    issue = 'wrong-email'
        else:
            raise ValueError("Resolvers Needs Update For New Category!")

        if issue:
            DataQualityIssue.objects.create(content_object=person,
                                            issue=issue,
                                            jurisdiction=patch.jurisdiction,
                                            message="Resolver over-ridden"
                                            )

            patch.status = 'deprecated'
            patch.save()
    return count
