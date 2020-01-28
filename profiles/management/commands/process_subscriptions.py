import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail


def process_query_sub(sub, since):
    """ given a query subscription, return a list of bills updated since then """
    pass


def process_bill_sub(sub, since):
    """ given a bill subscription, return bill if it was updated since then """
    if sub.bill.updated_at > since:
        return sub, sub.bill


def process_subs_for_user(user):
    if user.profile.alert_frequency == "daily":
        frequency = datetime.timedelta(hours=23)
    elif user.profile.alert_frequency == "weekly":
        frequency = datetime.timedelta(days=6)
    else:
        raise ValueError(user.profile.alert_frequency)
    last_checked = user.profile.last_checked
    subscriptions = list(user.subscriptions.filter(active=True))

    now = datetime.datetime.utcnow()

    print(
        f"processing {len(subscriptions)} for {user.email} "
        "({frequency}, last checked {last_checked})"
    )

    # not enough time passed
    if now - last_checked < frequency:
        return

    query_updates = []
    bill_updates = []

    for sub in subscriptions:
        if sub.subscription_type == "query":
            qu = process_query_sub(sub, last_checked)
            if qu:
                query_updates.append(qu)
        elif sub.subscription_type == "bill":
            bu = process_bill_sub(sub, last_checked)
            if bu:
                bill_updates.append(bu)
        else:
            raise ValueError(sub.subscription_type)

    return query_updates, bill_updates


def send_subscription_email(user, query_updates, bill_updates):
    if not bill_updates and not query_updates:
        raise ValueError("must have something to send")
    if not user.verified_email:
        return

    readable_when = (
        "this week" if user.profile.alert_frequency == "this week" else "today"
    )

    text_body = render_to_string(
        "alerts/alert_email.txt",
        {
            "user": user,
            "query_updates": query_updates,
            "bill_updates": bill_updates,
            "readable_when": readable_when,
        },
    )
    subject = f"Open States Alerts: {len(query_updates)+len(bill_updates)} updates"

    send_mail(
        subject,
        text_body,
        from_email="alerts@openstates.org",
        recipient_list=[user.verified_email],
    )


class Command(BaseCommand):
    help = "process subscriptions and send appropriate notifications"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        for user in User.objects.all():
            query_updates, bill_updates = process_subs_for_user(user)
            if query_updates or bill_updates:
                send_subscription_email(user, query_updates, bill_updates)
