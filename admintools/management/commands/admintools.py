from django.core.management.base import BaseCommand
from ...importers.people_orgs import person_issues


class Command(BaseCommand):
    help = 'Import Data Quality Issues into DB'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('import', nargs='+', type=str)

        # Optional arguments
        parser.add_argument(
            '--people',
            action='store_true',
            dest='people',
            default=False,
            help='ind Person Related Issues',
        )

    def handle(self, *args, **options):
        if options['people']:
            person_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported People'
                                                 ' DataQualityIssues into DB'))
