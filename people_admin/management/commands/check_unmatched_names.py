from django.core.management.base import BaseCommand
from utils.cli import yield_state_sessions
from ...utils import update_unmatched

# example command:
# docker-compose run --rm django poetry run ./manage.py check_unmatched_names va


class Command(BaseCommand):
    help = "check for unmatched names for people admin"

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("--session", default=None)

    def handle(self, *args, **options):
        for state, session in yield_state_sessions(
            options["state"], options["session"]
        ):
            n = update_unmatched(state, session)
            print(f"processed {n} unmatched people for {state} {session}")
