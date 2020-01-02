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


class PublicConfig(AppConfig):
    name = "public"

    def ready(self):
        from allauth.account.signals import email_confirmed

        email_confirmed.connect(create_key_for_verified_user)
