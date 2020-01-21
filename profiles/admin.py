from django.contrib import admin
from profiles.models import Profile, Subscription


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "subscription_type")
    autocomplete_fields = ("sponsor", "bill")
