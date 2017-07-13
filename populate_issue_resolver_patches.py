import os
import csv
import django


def populate():
    with open('sample-user-patches.csv') as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            person = Person.objects.get(id=row['person_id'])
            patch = IssueResolverPatch.objects.create(
                content_object=person,
                jurisdiction_id=row['jurisdiction_id'],
                status=row['status'],
                old_value=row['old_value'],
                new_value=row['new_value'],
                category=row['category'],
                alert=row['alert'],
                note=row['note'],
                source=row['source'],
                reporter_name=row['reporter_name'],
                reporter_email=row['reporter_email'],
                applied_by=row['applied_by']
            )
            patch.save()


if __name__ == '__main__':
    os.environ.get('DJANGO_SETTINGS_MODULE')
    django.setup()
    from admintools.models import IssueResolverPatch
    from opencivicdata.core.models import Person
    print("Starting Patches population script...")
    populate()
