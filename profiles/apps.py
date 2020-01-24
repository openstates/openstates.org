from django.apps import AppConfig


def create_key_for_verified_user(sender, **kwargs):
    from simplekeys.models import Key, Tier

    email = kwargs["email_address"]
    try:
        Key.objects.get(email=email.email)
    except Key.DoesNotExist:
        Key.objects.create(
            tier=Tier.objects.get(slug="default"),
            status="a",
            email=email.email,
            name=email.email,
        )


def create_profile(sender, instance, **kwargs):
    from profiles.models import Profile

    Profile.objects.get_or_create(user=instance)


class ProfilesConfig(AppConfig):
    name = "profiles"

    def ready(self):
        from allauth.account.signals import email_confirmed
        from django.db.models.signals import post_save
        from django.contrib.auth.models import User

        email_confirmed.connect(create_key_for_verified_user)
        post_save.connect(create_profile, sender=User)
