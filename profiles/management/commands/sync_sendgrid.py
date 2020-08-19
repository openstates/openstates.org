import os
import sendgrid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "sync users to sendgrid for newsletters"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])

        contacts = []

        for user in User.objects.all().select_related("profile"):
            verified_email = list(
                user.emailaddress_set.filter(primary=True, verified=True)
            )
            verified_email = verified_email[0] if verified_email else None
            is_suspended = user.profile.api_tier == "suspended"

            if verified_email and not is_suspended:
                contacts.append(
                    {
                        "email": verified_email.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    }
                )

        print(f"found {len(contacts)} contacts")

        CHUNK_SIZE = 800
        start = 0
        while start < len(contacts):
            print(f"pushing {start} to {start+CHUNK_SIZE}")
            try:
                sg.client.marketing.contacts.put(
                    request_body=dict(
                        list_ids=[], contacts=contacts[start : start + CHUNK_SIZE]
                    )
                )
            except Exception as e:
                print(e.body)
                raise
            start += CHUNK_SIZE
