import pytest
from django.contrib.auth.models import User
from graphapi.tests.utils import populate_db
from profiles.models import Subscription, Profile
from profiles.views import PermissionException
from opencivicdata.core.models import Person
from .test_models import COMPLEX_STR


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.fixture
def user():
    u = User.objects.create(username="testuser")
    Profile.objects.create(user=u, feature_subscriptions=True)
    return u


@pytest.mark.django_db
def test_add_search_subscription_no_perms(client):
    bu = User.objects.create(username="testuser")
    client.force_login(bu)
    with pytest.raises(PermissionException):
        client.post(
            "/accounts/profile/add_search_sub/", {"query": "topic", "state": "ak"}
        )
    assert Subscription.objects.count() == 0


@pytest.mark.django_db
def test_add_search_subscription_basic(client, user):
    client.force_login(user)
    resp = client.post(
        "/accounts/profile/add_search_sub/", {"query": "topic", "state": "ak"}
    )
    assert resp.status_code == 302
    assert Subscription.objects.count() == 1
    assert Subscription.objects.get().pretty == "Bills matching 'topic' from AK"

    resp = client.post(
        "/accounts/profile/add_search_sub/", {"query": "topic", "state": "ak"}
    )
    assert Subscription.objects.count() == 1


@pytest.mark.django_db
def test_add_search_subscription_complex(client, user):
    client.force_login(user)
    search_dict = {
        "query": "topic",
        "state": "ak",
        "chamber": "upper",
        "session": "2018",
        "classification": "bill",
        "subjects": ["MOOSE", "WILDLIFE"],
        "status": ["passed_lower"],
        "sponsor_id": Person.objects.get(name="Amanda Adams").id,
    }
    resp = client.post("/accounts/profile/add_search_sub/", search_dict)
    assert resp.status_code == 302
    assert Subscription.objects.count() == 1
    assert Subscription.objects.get().pretty == COMPLEX_STR


@pytest.mark.django_db
def test_add_sponsor_subscription(client, user):
    client.force_login(user)
    resp = client.post(
        "/accounts/profile/add_sponsor_sub/",
        {"sponsor_id": Person.objects.get(name="Amanda Adams").id},
    )
    assert resp.status_code == 302
    assert Subscription.objects.count() == 1
    assert Subscription.objects.get().pretty == "Bills sponsored by Amanda Adams"

    # ensure no duplication
    resp = client.post(
        "/accounts/profile/add_sponsor_sub/",
        {"sponsor_id": Person.objects.get(name="Amanda Adams").id},
    )
    assert Subscription.objects.count() == 1


@pytest.mark.django_db
def test_add_bill_subscription(client, user):
    client.force_login(user)
    resp = client.post("/accounts/profile/add_bill_sub/", {"bill_id": "ocd-bill/1"})
    assert resp.status_code == 302
    assert Subscription.objects.count() == 1
    assert Subscription.objects.get().pretty == "Updates on HB 1 in Alaska 2018"

    # ensure no duplication
    resp = client.post("/accounts/profile/add_bill_sub/", {"bill_id": "ocd-bill/1"})
    assert Subscription.objects.count() == 1


@pytest.mark.django_db
def test_deactivate_sub(client, user):
    sub = Subscription.objects.create(
        user=user, query="topic", state="ak", subjects=[], status=[]
    )

    client.force_login(user)
    resp = client.post("/accounts/profile/deactivate_sub/", {"subscription_id": sub.id})
    assert resp.status_code == 302
    # test that it is deactivated, not deleted
    assert Subscription.objects.count() == 1
    assert Subscription.objects.filter(active=True).count() == 0


@pytest.mark.django_db
def test_deactivate_subscription_other_user(client, user):
    other = User.objects.create(username="other")

    # isn't associated with the logged in user
    sub = Subscription.objects.create(
        user=other, query="topic", state="ak", subjects=[], status=[]
    )

    # deactivate fails
    client.force_login(user)
    resp = client.post("/accounts/profile/deactivate_sub/", {"subscription_id": sub.id})
    assert resp.status_code == 302
    assert Subscription.objects.filter(active=True).count() == 1


@pytest.mark.django_db
def test_reactivate_sub(client, user):
    Subscription.objects.create(
        user=user, query="topic", state="ak", subjects=[], status=[], active=False
    )

    # now use any of the add_*_sub methods
    client.force_login(user)
    client.post("/accounts/profile/add_search_sub/", {"query": "topic", "state": "ak"})
    assert Subscription.objects.filter(active=True).count() == 1
    assert Subscription.objects.get().pretty == "Bills matching 'topic' from AK"
