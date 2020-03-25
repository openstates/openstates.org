from django.core.management.base import BaseCommand
from ...models import Bundle
from utils.bills import search_bills


class Command(BaseCommand):
    help = "create simple bundle"

    def add_arguments(self, parser):
        parser.add_argument("search_term")
        parser.add_argument("--slug", required=True)
        parser.add_argument("--name", required=True)

    def handle(self, *args, **options):
        bills = list(search_bills(query=options["search_term"]))

        bundle = Bundle.objects.create(slug=options["slug"], name=options["name"])
        for b in bills:
            bundle.bills.add(b)

        print(f"created bundle {options['slug']} with {len(bills)} bills")
