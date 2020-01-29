import datetime
import pytz
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail
from ...models import DAILY, WEEKLY
from utils.bills import search_bills


def process_query_sub(sub, since):
    """ given a query subscription, return a list of bills updated since then """
    bills = list(
        search_bills(
            query=sub.query,
            state=sub.state,
            chamber=sub.chamber,
            session=sub.session,
            sponsor=sub.sponsor,
            classification=sub.classification,
            status=sub.status,
        )
        .filter(updated_at__gte=since)
        .order_by("-updated_at")
    )
    return bills


def process_bill_sub(sub, since):
    """ given a bill subscription, return bill if it was updated since then """
    if sub.bill.updated_at > since:
        return sub.bill


def process_subs_for_user(user):
    # these are just a little bit shorter than you'd expect because
    # if it has been 23ish hours since the last check or 6.5 days it still makes sense
    # to consider that time to update (given variability in when the cron runs, etc.)
    if user.profile.subscription_frequency == DAILY:
        frequency = datetime.timedelta(hours=23)
    elif user.profile.subscription_frequency == WEEKLY:
        frequency = datetime.timedelta(days=6)
    else:
        raise ValueError(user.profile.subscription_frequency)
    last_checked = user.profile.subscription_last_checked
    subscriptions = list(user.subscriptions.filter(active=True))

    now = pytz.utc.localize(datetime.datetime.utcnow())

    print(
        f"processing {len(subscriptions)} for {user.email} "
        f"({user.profile.get_subscription_frequency_display()}, last checked {last_checked})"
    )

    # not enough time passed
    if now - last_checked < frequency:
        return None, None

    query_updates = []
    bill_updates = []

    for sub in subscriptions:
        if sub.subscription_type == "query":
            bills = process_query_sub(sub, last_checked)
            if bills:
                query_updates.append((sub, bills))
        elif sub.subscription_type == "bill":
            bill = process_bill_sub(sub, last_checked)
            if bill:
                bill_updates.append(bill)
        else:
            raise ValueError(sub.subscription_type)

    return query_updates, bill_updates


def send_subscription_email(user, query_updates, bill_updates):
    if not bill_updates and not query_updates:
        raise ValueError("must have something to send")

    verified_email = user.emailaddress_set.filter(primary=True, verified=True)
    if not verified_email:
        raise ValueError("user does not have a verified email")

    text_body = render_to_string(
        "alerts/alert_email.txt",
        {"user": user, "query_updates": query_updates, "bill_updates": bill_updates},
    )

    update_count = len(query_updates) + len(bill_updates)
    updates = "update" if update_count == 1 else "updates"
    today = datetime.datetime.utcnow().strftime("%d %b %Y")
    if user.profile.subscription_frequency == DAILY:
        subject = f"Open States Daily Alert - {today}: {update_count} {updates}"
    else:
        subject = f"Open States Weekly Alert - {today}: {update_count} {updates}"

    send_mail(
        subject,
        text_body,
        from_email="alerts@openstates.org",
        recipient_list=[verified_email[0].email],
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
