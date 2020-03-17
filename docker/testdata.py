from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

u = User.objects.create_superuser("local", password="password", email="local@localhost")
u.profile.api_key = "testkey"
u.profile.api_tier = "unlimited"
u.profile.save()


# fb socialapp so that login page works
fb, _ = SocialApp.objects.get_or_create(
    provider="facebook", name="Facebook Placeholder", client_id="abc"
)
fb.sites.add(Site.objects.get())
