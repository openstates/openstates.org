from django.apps import AppConfig


def create_profile(sender, instance, **kwargs):
    from profiles.models import Profile

    Profile.objects.get_or_create(user=instance)


class ProfilesConfig(AppConfig):
    name = "profiles"

    def ready(self):
        from django.db.models.signals import post_save
        from django.contrib.auth.models import User

        post_save.connect(create_profile, sender=User)
