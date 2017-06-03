from django.core.management.base import BaseCommand
from ...importers import (person_issues, bills_issues,
                          vote_event_issues, orgs_issues)


class Command(BaseCommand):
    help = 'Import Data Quality Issues into DB'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('all', nargs='+', type=str)

        # Optional arguments
        parser.add_argument(
            '--all',
            action='store_true',
            dest='importall',
            default=False,
            help='import all Issues',
        )

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

        parser.add_argument(
            '--vote_events',
            action='store_true',
            dest='vote_event',
            default=False,
            help='import Vote Event Related Issues',
        )

        parser.add_argument(
            '--bills',
            action='store_true',
            dest='bills',
            default=False,
            help='import Bill Related Issues',
        )

    def handle(self, *args, **options):
        if options['importall']:
            person_issues()
            self.stdout.write(self.style.SQL_KEYWORD('Successfully Imported People'
                                                 ' DataQualityIssues into DB'))

            orgs_issues()
            self.stdout.write(self.style.SQL_KEYWORD('Successfully Imported Organization'
                                                 ' DataQualityIssues into DB'))

            vote_event_issues()
            self.stdout.write(self.style.SQL_KEYWORD('Successfully Imported VoteEvent'
                                                 ' DataQualityIssues into DB'))

            bills_issues()
            self.stdout.write(self.style.SQL_KEYWORD('Successfully Imported Bill'
                                                 ' DataQualityIssues into DB'))


            self.stdout.write(self.style.SUCCESS('Successfully Imported All'
                                                 ' DataQualityIssues into DB'))

        if options['people']:
            person_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported People'
                                                 ' DataQualityIssues into DB'))

        if options['organization']:
            orgs_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported Organization'
                                                 ' DataQualityIssues into DB'))

        if options['vote_event']:
            vote_event_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported VoteEvent'
                                                 ' DataQualityIssues into DB'))

        if options['bills']:
            bills_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported Bill'
                                                 ' DataQualityIssues into DB'))
