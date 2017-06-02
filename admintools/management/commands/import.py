from django.core.management.base import BaseCommand
from ...importers.people import person_issues
from ...importers.orgs import orgs_issues


class Command(BaseCommand):
    help = 'Import Data Quality Issues into DB'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('all', nargs='+', type=str)

        # Optional arguments
        parser.add_argument(
            '--people',
            action='store_true',
            dest='people',
            default=False,
            help='import Person Related Issues',
        )

        parser.add_argument(
            '--orgs',
            action='store_true',
            dest='organization',
            default=False,
            help='import Organization Related Issues',
        )

    def handle(self, *args, **options):
        if options['people']:
            person_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported People'
                                                 ' DataQualityIssues into DB'))

        if options['organization']:
            orgs_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported Organization'
                                                 ' DataQualityIssues into DB'))
