from django.core.management.base import BaseCommand
from ...resolvers.person import resolve_person_issues


class Command(BaseCommand):
    help = 'Import Issue Resolver Patches into DB'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('issues', nargs='+', type=str)

    def handle(self, *args, **options):
        resolve_person_issues()
        self.stdout.write(self.style.SUCCESS('Successfully Imported People'
                                             ' Issue Resolver Patches '
                                             'into DB'))
