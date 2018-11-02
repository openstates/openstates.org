import os
import json
import requests
from opencivicdata.core.models import Post
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'make JSON files for boundaries'

    def add_arguments(self, parser):
        parser.add_argument('state', help='name of state')
        parser.add_argument('year', help='year')

    def handle(self, *args, **options):
        dump_divisions(options['state'], options['year'])


def dump_divisions(state, year):
    posts = Post.objects.filter(organization__jurisdiction__name=state)
    for post in posts:
        division_id = post.division_id
        boundary = post.division.geometries.get(boundary__set__slug__in=(
            f'sldl-{year}', f'sldu-{year}')
        ).boundary
        boundary_url = 'http://beta.openstates.org' + boundary.get_absolute_url()

        # get the data and write the file
        meta = requests.get(boundary_url).json()
        shape = requests.get(boundary_url + 'simple_shape').json()

        output = {
            'division_id': division_id,
            'year': f'20{year}',
            'metadata': meta['metadata'],
            'centroid': meta['centroid'],
            'extent': meta['extent'],
            'shape': shape,
        }

        filename = f'20{year}/{division_id}.json'

        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

        with open(filename, 'w') as f:
            json.dump(output, f)
