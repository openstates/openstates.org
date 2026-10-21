from django.apps import AppConfig


def create_profile(sender, instance, **kwargs):
    from profiles.models import Profile

    Profile.objects.get_or_create(user=instance)


class ProfilesConfig(AppConfig):
    name = "profiles"

    def ready(self):
        from django.contrib.auth.models import User
        from django.db.models.signals import post_save

        post_save.connect(create_profile, sender=User)
