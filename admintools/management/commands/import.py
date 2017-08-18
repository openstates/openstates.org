from django.core.management.base import BaseCommand
from ...importers import (people_issues, bills_issues, memberships_issues,
                          vote_events_issues, organizations_issues,
                          posts_issues)


class Command(BaseCommand):
    help = 'Import Data Quality Issues into DB'

    def add_arguments(self, parser):

        # Optional arguments
        parser.add_argument(
            '--people',
            action='store_true',
            dest='people',
            default=False,
            help='import Person Related Issues',
        )

        parser.add_argument(
            '--organizations',
            action='store_true',
            dest='organization',
            default=False,
            help='import Organization Related Issues',
        )

        parser.add_argument(
            '--memberships',
            action='store_true',
            dest='membership',
            default=False,
            help='import Membership Related Issues',
        )

        parser.add_argument(
            '--posts',
            action='store_true',
            dest='post',
            default=False,
            help='import Post Related Issues',
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
        if True not in [options['people'], options['organization'],
                        options['vote_event'], options['bills'],
                        options['membership'], options['post']]:
                options['people'] = True
                options['organization'] = True
                options['vote_event'] = True
                options['bills'] = True
                options['membership'] = True
                options['post'] = True

        if options['people']:
            people_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported People'
                                                 ' DataQualityIssues into DB'))

        if options['organization']:
            organizations_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported '
                                                 'Organization'
                                                 ' DataQualityIssues into DB'))

        if options['membership']:
            memberships_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported '
                                                 'Membership'
                                                 ' DataQualityIssues into DB'))

        if options['post']:
            posts_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported '
                                                 'Post'
                                                 ' DataQualityIssues into DB'))

        if options['vote_event']:
            vote_events_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported '
                                                 'VoteEvent'
                                                 ' DataQualityIssues into DB'))

        if options['bills']:
            bills_issues()
            self.stdout.write(self.style.SUCCESS('Successfully Imported Bill'
                                                 ' DataQualityIssues into DB'))
