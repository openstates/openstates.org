from django.core.management.base import BaseCommand
from opencivicdata.core.models import Jurisdiction
from ...reports import (people_report, bills_report, memberships_report,
                        vote_events_report, organizations_report, posts_report)


class Command(BaseCommand):
    help = 'Import Data Quality Issues into DB'

    def add_arguments(self, parser):
        parser.add_argument(
            'jurisdictions',
            type=str, nargs='+',
            help='jurisdiction to import'
        )

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
        # if no flags are passed, we'll do all reports
        if not any([options['people'], options['organization'],
                    options['vote_event'], options['bills']]):
                options['people'] = True
                options['organization'] = True
                options['vote_event'] = True
                options['bills'] = True

        for jname in options['jurisdictions']:
            try:
                jur = Jurisdiction.objects.get(id__contains=':' + jname + '/')
            except Jurisdiction.DoesNotExist:
                self.stderr.write(self.style.ERROR("no such jurisdiction: " + jname))
                return

            if options['people']:
                people_report(jur)
                memberships_report(jur)
                posts_report(jur)
            if options['organization']:
                organizations_report(jur)
            if options['vote_event']:
                vote_events_report(jur)
            if options['bills']:
                bills_report(jur)
