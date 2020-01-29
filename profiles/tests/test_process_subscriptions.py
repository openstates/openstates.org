import datetime
import pytz
import pytest
from django.contrib.auth.models import User
from graphapi.tests.utils import populate_db
from profiles.models import Subscription
from opencivicdata.legislative.models import Bill
from ..management.commands.process_subscriptions import (
    process_bill_sub,
    process_query_sub,
    process_subs_for_user,
    send_subscription_email,
    DAILY,
)


@pytest.mark.django_db
def setup():
    populate_db()


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


@pytest.mark.django_db
def test_process_bill_sub(user):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription(user=user, bill=hb1)

    now = datetime.datetime.now()
    now = pytz.utc.localize(now)
    yesterday = now - datetime.timedelta(days=1)

    # no changes since now
    assert process_bill_sub(sub, now) is None

    # bill changed in last day
    assert process_bill_sub(sub, yesterday) == hb1


@pytest.mark.django_db
def test_process_query_sub_simple(user):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription(user=user, query="moose")

    now = datetime.datetime.now()
    now = pytz.utc.localize(now)
    yesterday = now - datetime.timedelta(days=1)

    # no changes since now
    assert process_query_sub(sub, now) is None

    # bill changed in last day
    assert process_query_sub(sub, yesterday) == [hb1]


@pytest.mark.django_db
def test_process_subs_for_user_simple(user):
    hb1 = Bill.objects.get(identifier="HB 1")

    # last check is more than a day ago
    query_updates, bill_updates = process_subs_for_user(user)
    assert query_updates == []
    assert bill_updates == [hb1]

    # we're within a week now
    user.profile.subscription_last_checked = pytz.utc.localize(datetime.datetime.now())
    user.profile.save()
    query_updates, bill_updates = process_subs_for_user(user)
    assert query_updates is None
    assert bill_updates is None


@pytest.mark.django_db
def test_process_subs_for_user_query(user):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription.objects.create(user=user, subjects=[], status=[], query="moose")

    # last check is more than a day ago
    query_updates, bill_updates = process_subs_for_user(user)
    assert bill_updates == []
    assert query_updates == [(sub, [hb1])]

    # we're within a week now
    user.profile.subscription_last_checked = pytz.utc.localize(datetime.datetime.now())
    user.profile.save()
    query_updates, bill_updates = process_subs_for_user(user)
    assert query_updates is None
    assert bill_updates is None


@pytest.mark.django_db
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
    assert "https://openstates.org/accounts/unsubscribe/" in msg.body


@pytest.mark.django_db
def test_send_email_simple_bill_daily(user, mailoutbox):
    hb1 = Bill.objects.get(identifier="HB 1")

    user.profile.subscription_frequency = DAILY
    user.profile.save()

    bill_updates = [hb1]
    send_subscription_email(user, [], bill_updates)

    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert "Daily Alert" in msg.subject
    assert msg.subject.endswith("1 update")
    assert "This is your daily automated alert from OpenStates.org." in msg.body


@pytest.mark.django_db
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
    print(msg.body)
    assert (
        "Bills matching 'moose' from all states - 1 new bills - https://openstates.org/search/?query=moose"
        in msg.body
    )
    assert (
        "HB 1 - Moose Freedom Act (Alaska 2018) - https://openstates.org/ak/bills/2018/HB1/"
        in msg.body
    )
    assert "https://openstates.org/accounts/unsubscribe/" in msg.body


@pytest.mark.django_db
def test_send_email_simple_bill_no_updates(user, mailoutbox):
    with pytest.raises(ValueError):
        send_subscription_email(user, [], [])


@pytest.mark.django_db
def test_send_email_simple_bill_no_email(user, mailoutbox):
    hb1 = Bill.objects.get(identifier="HB 1")
    sub = Subscription.objects.create(
        user=user, bill=hb1, subjects=[], status=[], query=""
    )
    bill_updates = [(sub, hb1)]

    # can't send without a verified email
    user.emailaddress_set.update(verified=False)
    with pytest.raises(ValueError):
        send_subscription_email(user, [], bill_updates)
