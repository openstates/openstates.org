from django.db import transaction
from django.core.management.base import BaseCommand
from opencivicdata.legislative.models import Bill
import pymongo
from ...models import LegacyBillMapping
from ...utils import jid_to_abbr


class Command(BaseCommand):
    help = 'load in legacy bill ids'

    def add_arguments(self, parser):
        parser.add_argument('mongo_host')

    def handle(self, *args, **options):
        db = pymongo.MongoClient(options['mongo_host'])['fiftystates']

        # (state, chamber, bill_id): openstates_id
        legacy_mapping = {}
        new_mapping = {}

        old_bills = db.bills.find()
        for b in old_bills:
            legacy_mapping[(b['state'], b['chamber'], b['session'], b['bill_id'])] = b['_id']

        print(len(legacy_mapping), len(new_mapping))

        for b in Bill.objects.all():
            session = b.legislative_session.identifier
            state = jid_to_abbr(b.legislative_session.jurisdiction_id)
            chamber = b.from_organization.classification
            if chamber == 'legislature' and state in ('ne', 'dc'):
                chamber = 'upper'
            new_mapping[(state, chamber, session, b.identifier)] = b.id

        print(len(legacy_mapping), len(new_mapping))

        objects = []
        for key, bill_id in new_mapping.items():
            try:
                objects.append(LegacyBillMapping(legacy_id=legacy_mapping[key],
                                                 bill_id=bill_id))
            except KeyError:
                print('no mapping for', key)

        with transaction.atomic():
            LegacyBillMapping.objects.bulk_create(objects)
