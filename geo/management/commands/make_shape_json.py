import os
import json
from django.core.management.base import BaseCommand
from openstates.data.models import Post


class Command(BaseCommand):
    help = "make JSON files for boundaries"

    def add_arguments(self, parser):
        parser.add_argument("year", help="year")
        parser.add_argument("--state", help="name of state")

    def handle(self, *args, **options):
        dump_divisions(options["year"], options["state"])


def dump_divisions(year, state=None):
    if state:
        posts = Post.objects.filter(organization__jurisdiction__name=state)
    else:
        posts = Post.objects.filter(
            organization__classification__in=("upper", "lower", "legislature")
        )
    short_year = year[-2:]
    for post in posts:
        division_id = post.division_id
        try:
            boundary = post.division.geometries.get(
                boundary__set__slug__in=(
                    f"sldl-{short_year}",
                    f"sldu-{short_year}",
                    "nh-12",
                )
            ).boundary
        except Exception:
            print(division_id, "does not exist")
            continue

        output = {
            "division_id": division_id,
            "year": year,
            "metadata": boundary.metadata,
            "centroid": json.loads(boundary.centroid.geojson),
            "extent": boundary.extent,
            # shape is about 8 times larger
            "shape": json.loads(boundary.simple_shape.geojson),
        }

        filename = f"{year}/{division_id}.json"

        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        with open(filename, "w") as f:
            json.dump(output, f, sort_keys=True, indent=1)
