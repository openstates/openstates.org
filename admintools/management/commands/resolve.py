from django.core.management.base import BaseCommand
from ...resolvers.person import apply_person_patches


class Command(BaseCommand):
    help = 'Import Issue Resolver Patches into DB'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('issues', nargs='+', type=str)

    def handle(self, *args, **options):
        apply_person_patches()
        self.stdout.write(self.style.SUCCESS('Successfully Imported People'
                                             ' Issue Resolver Patches '
                                             'into DB'))
