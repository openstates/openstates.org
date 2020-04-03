import re
from django.db import transaction
from django.core.management.base import BaseCommand
from ...models import DivisionGeometry
from openstates.divisions import Division
from boundaries.models import BoundarySet


BOUNDARY_MAPPINGS = {
    "sldl-18": {"key": "census_geoid_14", "prefix": "sldl-", "ignore": ".*ZZZ"},
    "sldl-17": {"key": "census_geoid_14", "prefix": "sldl-", "ignore": ".*ZZZ"},
    "sldu-18": {"key": "census_geoid_14", "prefix": "sldu-", "ignore": ".*ZZZ"},
    "sldu-17": {"key": "census_geoid_14", "prefix": "sldu-", "ignore": ".*ZZZ"},
    "nh-12": {"key": "census_geoid_14", "prefix": "sldl-", "ignore": ".*zzz"},
}


def load_mapping(
    boundary_set_id, key, prefix, boundary_key="external_id", ignore=None, quiet=False
):
    if ignore:
        ignore = re.compile(ignore)
    ignored = 0
    geoid_mapping = {}

    division_geometries = []

    for div in Division.get("ocd-division/country:us").children(levels=100):
        if div.attrs[key]:
            geoid_mapping[div.attrs[key]] = div.id
        else:
            geoid_mapping[div.id] = div.id

    print("processing", boundary_set_id)

    boundary_set = BoundarySet.objects.get(pk=boundary_set_id)
    if callable(boundary_key):
        fields = []
    else:
        fields = [boundary_key]
    for boundary in boundary_set.boundaries.values("id", "name", *fields):
        if callable(boundary_key):
            boundary_property = boundary_key(boundary)
        else:
            boundary_property = boundary[boundary_key]
        ocd_id = geoid_mapping.get(prefix + boundary_property)
        if ocd_id:
            division_geometries.append(
                DivisionGeometry(division_id=ocd_id, boundary_id=boundary["id"])
            )
        elif not ignore or not ignore.match(boundary["name"]):
            if not quiet:
                print("unmatched external id", boundary["name"], boundary_property)
        else:
            ignored += 1

    DivisionGeometry.objects.bulk_create(division_geometries)

    if ignored:
        print("ignored {} unmatched external ids".format(ignored))


class Command(BaseCommand):
    help = "load in division-boundary mappings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--quiet",
            action="store_true",
            dest="quiet",
            default=False,
            help="Be somewhat quiet.",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            DivisionGeometry.objects.all().delete()
            for set_id, d in BOUNDARY_MAPPINGS.items():
                load_mapping(set_id, quiet=options["quiet"], **d)
