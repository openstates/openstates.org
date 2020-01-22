import pytest
from django.contrib.auth.models import User
from graphapi.tests.utils import populate_db
from opencivicdata.core.models import Person
from profiles.models import Subscription

COMPLEX_STR = (
    "Bills matching 'topic' from AK, upper chamber, "
    "classified as bill, including subjects 'MOOSE, WILDLIFE', "
    "status includes 'passed_lower', sponsored by Amanda Adams"
)


@pytest.mark.django_db
def setup():
    populate_db()


def _one_of_each():
    user = User.objects.create(username="testuser")
    bs = Subscription(user=user, bill_id="ocd-bill/1")
    qs = Subscription(user=user, query="topic", state="ak")
    ss = Subscription(user=user, sponsor=Person.objects.get(name="Amanda Adams"))
    return bs, qs, ss


@pytest.mark.django_db
def test_subscription_type():
    bs, qs, ss = _one_of_each()
    assert bs.subscription_type == "bill"
    assert qs.subscription_type == "query"
    assert ss.subscription_type == "sponsor"


@pytest.mark.django_db
def test_subscription_pretty():
    bs, qs, ss = _one_of_each()
    assert bs.pretty == "Updates on HB 1 in Alaska 2018"
    assert qs.pretty == "Bills matching 'topic' from AK"
    assert ss.pretty == "Bills sponsored by Amanda Adams"


@pytest.mark.django_db
def test_complex_pretty():
    cs = Subscription(
        query="topic",
        state="ak",
        chamber="upper",
        classification="bill",
        subjects=["MOOSE", "WILDLIFE"],
        status=["passed_lower"],
        sponsor=Person.objects.get(name="Amanda Adams"),
    )
    assert cs.pretty == COMPLEX_STR


@pytest.mark.django_db
def test_subscription_site_url():
    bs, qs, ss = _one_of_each()
    assert bs.site_url == "/ak/bills/2018/HB1/"
    assert (
        qs.site_url
        == "/ak/bills/?query=topic&session=&chamber=&classification=&sponsor_id="
    )
    assert ss.site_url.startswith("/person/amanda-adams")
