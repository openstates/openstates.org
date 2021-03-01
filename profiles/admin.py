from django.contrib import admin
from profiles.models import Profile, Subscription, Notification


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "api_tier")
    search_fields = ("user__email", "api_key")
    list_filter = ("api_tier",)

    def email(self, p):
        return p.user.email


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "subscription_type", "active")
    list_filter = ("active",)
    autocomplete_fields = ("sponsor", "bill")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "sent", "num_bill_updates", "num_query_updates")
    search_fields = ("email",)
    ordering = ("sent",)
    date_hierarchy = "sent"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
