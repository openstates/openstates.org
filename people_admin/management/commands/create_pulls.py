from django.core.management.base import BaseCommand
from people_admin.models import DeltaSet, PullStatus
from people_admin.git import delta_set_to_pr


class Command(BaseCommand):
    help = "create pull requests from deltas"

    def add_arguments(self, parser):
        parser.add_argument("--list", default=False, action="store_true")
        parser.add_argument("--delta")

    def handle(self, *args, **options):
        nothing = True
        if options["list"]:
            nothing = False
            to_create = DeltaSet.objects.filter(
                pr_status=PullStatus.NOT_CREATED
            ).order_by("id")
            for ds in to_create:
                print(f"{ds.id} | {ds.name} | {ds.created_by}")
        if options["delta"]:
            nothing = False
            ds = DeltaSet.objects.get(
                pk=options["delta"], pr_status=PullStatus.NOT_CREATED
            )
            print(f"creating {ds.id} | {ds.name} | {ds.created_by}")
            ds.pr_url = delta_set_to_pr(ds)
            ds.pr_status = PullStatus.CREATED
            ds.save()
        if nothing:
            print("must either pass --list or --delta parameters")
