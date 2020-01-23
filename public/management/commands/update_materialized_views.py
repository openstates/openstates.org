from django.core.management.base import BaseCommand
from django.db import transaction, connection


class Command(BaseCommand):
    help = "update materialized views"

    def add_arguments(self, parser):
        parser.add_argument("--initial", action="store_true")

    def handle(self, *args, **options):
        concurrent = "CONCURRENTLY"

        # initial run can't be concurrent
        if options["initial"]:
            concurrent = ""

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    f"REFRESH MATERIALIZED VIEW {concurrent} public_billstatus"
                )
