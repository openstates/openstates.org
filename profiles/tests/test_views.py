import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from graphapi.tests.utils import populate_db
from opencivicdata.core.models import Person
from profiles.models import Subscription, Notification
from profiles.views import PermissionException
from profiles.utils import utcnow
from .test_models import COMPLEX_STR


@pytest.mark.django_db
def setup():
    populate_db()


@pytest.fixture
def user():
    u = User.objects.create(username="testuser", email="valid@example.com")
    u.profile.feature_subscriptions = True
    u.profile.save()
    return u


@pytest.mark.django_db
def test_add_search_subscription_no_perms(client):
    bu = User.objects.create(username="testuser")
    bu.profile.feature_subscriptions = False
    bu.profile.save()
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
def test_add_search_subscription_no_query(client, user):
    client.force_login(user)
    resp = client.post(
        "/accounts/profile/add_search_sub/", {"query": "", "state": "ak"}
    )
    assert resp.status_code == 400
    assert Subscription.objects.count() == 0


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


@pytest.mark.django_db
def test_bill_subscription_add(client, user):
    client.force_login(user)
    resp = client.post(
        "/accounts/profile/bill_sub/",
        {"bill_id": "ocd-bill/1"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json() == {"error": "", "bill_id": "ocd-bill/1", "active": True}
    assert Subscription.objects.count() == 1
    assert Subscription.objects.get().pretty == "Updates on HB 1 in Alaska 2018"

    # ensure no duplication
    resp = client.post(
        "/accounts/profile/bill_sub/",
        {"bill_id": "ocd-bill/1"},
        content_type="application/json",
    )
    assert resp.json() == {"error": "", "bill_id": "ocd-bill/1", "active": True}
    assert Subscription.objects.count() == 1


@pytest.mark.django_db
def test_bill_subscription_get(client, user):
    client.force_login(user)

    # doesn't exist
    resp = client.get("/accounts/profile/bill_sub/", {"bill_id": "ocd-bill/1"})
    assert resp.status_code == 200
    assert resp.json() == {"error": "", "bill_id": "ocd-bill/1", "active": False}

    Subscription.objects.create(user=user, bill_id="ocd-bill/1", subjects=[], status=[])
    resp = client.get("/accounts/profile/bill_sub/", {"bill_id": "ocd-bill/1"})
    assert resp.status_code == 200
    assert resp.json() == {"error": "", "bill_id": "ocd-bill/1", "active": True}


@pytest.mark.django_db
def test_bill_subscription_delete(client, user):
    client.force_login(user)

    # doesn't exist
    resp = client.delete(
        "/accounts/profile/bill_sub/",
        {"bill_id": "ocd-bill/1"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "error": "no such subscription",
        "bill_id": "ocd-bill/1",
        "active": False,
    }

    Subscription.objects.create(user=user, bill_id="ocd-bill/1", subjects=[], status=[])
    resp = client.delete(
        "/accounts/profile/bill_sub/",
        {"bill_id": "ocd-bill/1"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json() == {"error": "", "bill_id": "ocd-bill/1", "active": False}
    assert Subscription.objects.filter(active=False).count() == 1


@pytest.mark.django_db
def test_unsubscribe_logged_in(client, user):
    client.force_login(user)

    Subscription.objects.create(user=user, bill_id="ocd-bill/1", subjects=[], status=[])
    resp = client.get("/accounts/profile/unsubscribe/")
    assert resp.status_code == 200
    assert len(resp.context["subscriptions"]) == 1
    assert Subscription.objects.filter(active=True).count() == 1

    resp = client.post("/accounts/profile/unsubscribe/")
    assert resp.status_code == 302
    assert Subscription.objects.filter(active=True).count() == 0
    assert Subscription.objects.filter(active=False).count() == 1


@pytest.mark.django_db
def test_unsubscribe_email_param(client, user):
    Subscription.objects.create(user=user, bill_id="ocd-bill/1", subjects=[], status=[])
    nobj = Notification.objects.create(
        email=user.email, sent=utcnow(), num_query_updates=0, num_bill_updates=0
    )

    resp = client.get(f"/accounts/profile/unsubscribe/?email={nobj.id}")
    assert resp.status_code == 200
    assert len(resp.context["subscriptions"]) == 1
    assert Subscription.objects.filter(active=True).count() == 1

    resp = client.post(f"/accounts/profile/unsubscribe/?email={nobj.id}")
    assert resp.status_code == 302
    assert Subscription.objects.filter(active=True).count() == 0
    assert Subscription.objects.filter(active=False).count() == 1


@pytest.mark.django_db
def test_unsubscribe_access_denied(client, user):
    resp = client.get("/accounts/profile/unsubscribe/")
    assert resp.status_code == 302


@pytest.mark.django_db
def test_request_key_success(client, user):
    client.force_login(user)
    user.emailaddress_set.create(email="test@example.com", primary=True, verified=True)
    assert user.profile.api_tier == "inactive"
    resp = client.post("/accounts/profile/request_key/")
    messages = list(get_messages(resp.wsgi_request))
    assert messages[0].level_tag == "success"
    refreshed_user = User.objects.get()
    assert refreshed_user.profile.api_tier == "default"


@pytest.mark.django_db
def test_request_key_errors(client, user):
    # not logged in
    resp = client.post("/accounts/profile/request_key/")
    assert resp.status_code == 302

    # no valid email
    client.force_login(user)
    resp = client.post("/accounts/profile/request_key/")
    messages = list(get_messages(resp.wsgi_request))
    assert messages[0].level_tag == "warning"
    refreshed_user = User.objects.get()
    assert refreshed_user.profile.api_tier == "inactive"

    # valid email, but suspended
    user.emailaddress_set.create(email="test@example.com", primary=True, verified=True)
    user.profile.api_tier = "suspended"
    user.profile.save()
    client.force_login(user)
    resp = client.post("/accounts/profile/request_key/")
    messages = list(get_messages(resp.wsgi_request))
    assert messages[0].level_tag == "warning"
    refreshed_user = User.objects.get()
    assert refreshed_user.profile.api_tier == "suspended"
