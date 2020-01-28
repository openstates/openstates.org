import datetime
import pytz
import pytest
from django.contrib.auth.models import User
from graphapi.tests.utils import populate_db
from profiles.models import Subscription
from opencivicdata.legislative.models import Bill
from ..management.commands.process_subscriptions import process_bill_sub


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.fixture
def user():
    u = User.objects.create(username="testuser")
    u.profile.feature_subscriptions = True
    u.profile.save()
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
    assert process_bill_sub(sub, yesterday) == (sub, hb1)
