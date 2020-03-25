from django.core.management.base import BaseCommand
from ...models import Bundle
from utils.bills import search_bills


class Command(BaseCommand):
    help = "bundle management"

    def add_arguments(self, parser):
        parser.add_argument("slug")
        parser.add_argument("--name")
        parser.add_argument("--search")

    def handle(self, *args, **options):
        bundle, created = Bundle.objects.get_or_create(
            slug=options["slug"], defaults=dict(name=options["name"])
        )

        bills = list(search_bills(query=options["search"]))

        for b in bills:
            bundle.bills.add(b)

        if created:
            print(f"created bundle {options['slug']} with {len(bills)} bills")
        else:
            print(f"updated bundle {options['slug']} with {len(bills)} bills")
