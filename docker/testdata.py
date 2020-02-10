from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from simplekeys.models import Tier, Zone, Key
from allauth.socialaccount.models import SocialApp

User.objects.create_superuser("local", password="password", email="local@localhost")

tier, _ = Tier.objects.get_or_create(name="default", slug="default")

for name in ("default", "geo", "graphapi"):
    zone, _ = Zone.objects.get_or_create(name=name, slug=name)
    zone.limits.create(
        tier=tier,
        quota_period="d",
        quota_requests=100000,
        requests_per_second=100000,
        burst_size=100000,
    )

Key.objects.get_or_create(
    key="testkey", status="a", tier=tier, email="local@localhost", name="local"
)

# fb socialapp so that login page works
fb, _ = SocialApp.objects.get_or_create(
    provider="facebook", name="Facebook Placeholder", client_id="abc"
)
fb.sites.add(Site.objects.get())
