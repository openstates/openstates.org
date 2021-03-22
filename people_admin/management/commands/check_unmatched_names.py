from django.core.management.base import BaseCommand
from utils.cli import yield_state_sessions
from ...unmatched import update_unmatched, unmatched_to_deltas

# example command:
# docker-compose run --rm django poetry run ./manage.py check_unmatched_names va


class Command(BaseCommand):
    help = "check for unmatched names for people admin"

    def add_arguments(self, parser):
        parser.add_argument("state")
        parser.add_argument("--session", default=None)

    def handle(self, *args, **options):
        states = set()
        for state, session in yield_state_sessions(
            options["state"], options["session"]
        ):
            unmatched = update_unmatched(state, session)
            print(f"processed {unmatched} unmatched people for {state} {session}")
            # keep list of states around for delta processing
            states.add(state)

        for state in sorted(states):
            matched = unmatched_to_deltas(state)
            print(
                f"updating {state} legislator matching DeltaSet with {matched} people"
            )
