from django.core.management.base import BaseCommand
from django.db import transaction, connection


class Command(BaseCommand):
    help = "update materialized views"

    def handle(self, *args, **options):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "REFRESH MATERIALIZED VIEW CONCURRENTLY public_billstatus"
                )
