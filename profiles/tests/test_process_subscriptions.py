import pytz
import datetime
import pytest
from django.contrib.auth.models import User
from profiles.models import Subscription
from openstates.data.models import Bill
from ..models import Notification
from ..utils import utcnow
from ..management.commands.process_subscriptions import (
    process_bill_sub,
    process_query_sub,
    process_subs_for_user,
    send_subscription_email,
    DAILY,
    SkipCheck,
)


@pytest.fixture
def user():
    u = User.objects.create(username="testuser")
    u.profile.feature_subscriptions = True
    u.profile.subscription_last_checked = pytz.utc.localize(
        datetime.datetime(2020, 1, 1)
    )
    u.profile.save()
    u.emailaddress_set.create(email="valid@example.com", verified=True, primary=True)
    return u


def test_process_bill_sub(user):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription(user=user, bill=hb1)

    now = utcnow()
    yesterday = now - datetime.timedelta(days=1)
    hb1.latest_action_date = yesterday.strftime("%Y-%m-%d")
    hb1.save()

    # no changes since now
    assert process_bill_sub(sub, now) is None

    # bill changed in last day
    assert process_bill_sub(sub, yesterday) == hb1


def test_process_bill_sub_future(user):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription(user=user, bill=hb1)

    now = utcnow()
    yesterday = now - datetime.timedelta(days=1)
    tomorrow = now + datetime.timedelta(days=1)
    hb1.latest_action_date = tomorrow.strftime("%Y-%m-%d")
    hb1.save()

    # no changes since now
    assert process_bill_sub(sub, now) is None

    # bill changed in last day
    assert process_bill_sub(sub, yesterday) is None


def test_process_query_sub_simple(user):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription(user=user, query="moose")

    now = utcnow()
    yesterday = now - datetime.timedelta(days=1)

    # no changes since now
    assert process_query_sub(sub, now) == []

    # bill changed in last day
    assert process_query_sub(sub, yesterday) == [hb1]


def test_process_subs_for_user_simple(user):
    hb1 = Bill.objects.get(identifier="HB 1")
    hb1.latest_action_date = datetime.date.today().strftime("%Y-%m-%d")
    hb1.save()
    Subscription.objects.create(user=user, subjects=[], status=[], bill=hb1)

    # last check is more than a day ago
    query_updates, bill_updates = process_subs_for_user(user)
    assert query_updates == []
    assert bill_updates == [hb1]

    # we're within a week now
    user.profile.subscription_last_checked = utcnow()
    user.profile.save()
    with pytest.raises(SkipCheck):
        query_updates, bill_updates = process_subs_for_user(user)


def test_process_subs_for_user_query(user):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription.objects.create(user=user, subjects=[], status=[], query="moose")

    # last check is more than a day ago
    query_updates, bill_updates = process_subs_for_user(user)
    assert bill_updates == []
    assert query_updates == [(sub, [hb1])]

    # we're within a week now
    user.profile.subscription_last_checked = utcnow()
    user.profile.save()
    with pytest.raises(SkipCheck):
        query_updates, bill_updates = process_subs_for_user(user)


def test_send_email_simple_bill_weekly(user, mailoutbox):
    hb1 = Bill.objects.get(identifier="HB 1")
    bill_updates = [hb1]

    send_subscription_email(user, [], bill_updates)

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert "Weekly Alert" in msg.subject
    assert msg.subject.endswith("1 update")
    assert "This is your weekly automated alert from OpenStates.org." in msg.body
    assert "1 of your tracked bills had new activity" in msg.body
    assert (
        "HB 1 - Moose Freedom Act (Alaska 2018) - https://openstates.org/ak/bills/2018/HB1/"
        in msg.body
    )
    assert len(msg.alternatives) == 1
    html, media_type = msg.alternatives[0]
    assert media_type == "text/html"
    assert (
        '<a href="https://openstates.org/ak/bills/2018/HB1/">HB 1 - Moose Freedom Act (Alaska 2018)</a>'
        in html
    )

    # check that record was created
    nobj = Notification.objects.get()
    assert nobj.num_query_updates == 0
    assert nobj.num_bill_updates == 1
    assert nobj.email == "valid@example.com"

    assert (
        f"https://openstates.org/accounts/profile/unsubscribe/?email={nobj.id}"
        in msg.body
    )
    assert (
        f"https://openstates.org/accounts/profile/unsubscribe/?email={nobj.id}" in html
    )


def test_send_email_simple_bill_daily_no_html(user, mailoutbox):
    # test some profile variation
    hb1 = Bill.objects.get(identifier="HB 1")

    user.profile.subscription_frequency = DAILY
    user.profile.subscription_emails_html = False
    user.profile.save()

    bill_updates = [hb1]
    send_subscription_email(user, [], bill_updates)

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert "Daily Alert" in msg.subject
    assert msg.subject.endswith("1 update")
    assert "This is your daily automated alert from OpenStates.org." in msg.body


def test_send_email_from_query(user, mailoutbox):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription.objects.create(user=user, subjects=[], status=[], query="moose")
    query_updates = [(sub, [hb1])]
    send_subscription_email(user, query_updates, [])

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert "Weekly Alert" in msg.subject
    assert msg.subject.endswith("1 update")
    assert "This is your weekly automated alert from OpenStates.org." in msg.body
    assert "1 of your tracked queries had new legislation" in msg.body
    assert (
        "Bills matching 'moose' from all states - 1 new bills - https://openstates.org/search/?query=moose"
        in msg.body
    )
    assert (
        "HB 1 - Moose Freedom Act (Alaska 2018) - https://openstates.org/ak/bills/2018/HB1/"
        in msg.body
    )

    nobj = Notification.objects.get()
    assert nobj.num_query_updates == 1
    assert nobj.num_bill_updates == 0
    assert nobj.email == "valid@example.com"


def test_send_email_simple_bill_no_updates(user, mailoutbox):
    with pytest.raises(ValueError):
        send_subscription_email(user, [], [])
    assert Notification.objects.count() == 0


def test_send_email_simple_bill_no_email(user, mailoutbox):
    hb1 = Bill.objects.get(identifier="HB 1")
    hb1.latest_action_date = datetime.date.today().strftime("%Y-%m-%d")
    hb1.save()
    sub = Subscription.objects.create(
        user=user, bill=hb1, subjects=[], status=[], query=""
    )
    bill_updates = [(sub, hb1)]

    # can't send without a verified email
    user.emailaddress_set.update(verified=False)
    with pytest.raises(SkipCheck):
        send_subscription_email(user, [], bill_updates)
    assert Notification.objects.count() == 0


def test_send_email_simple_dry_run(user, mailoutbox):
    hb1 = Bill.objects.get(identifier="HB 1")
    hb1.latest_action_date = datetime.date.today().strftime("%Y-%m-%d")
    hb1.save()
    sub = Subscription.objects.create(user=user, subjects=[], status=[], query="moose")
    query_updates = [(sub, [hb1])]
    send_subscription_email(user, query_updates, [], dry_run=True)
    assert Notification.objects.count() == 0
