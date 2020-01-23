from django.contrib.auth.models import User
from simplekeys.models import Tier, Zone, Key


User.objects.create_superuser("local", password="password", email="local@localhost")

tier, _ = Tier.objects.get_or_create(name="local", slug="local")

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
