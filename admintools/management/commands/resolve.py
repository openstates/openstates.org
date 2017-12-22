from django.core.management.base import BaseCommand
from ...resolvers.person import setup_person_resolver


class Command(BaseCommand):
    help = 'Import Issue Resolver Patches into DB'

    def handle(self, *args, **options):
        setup_person_resolver()
        self.stdout.write(self.style.SUCCESS('Successfully Imported People'
                                             ' Issue Resolver Patches '
                                             'into DB'))
