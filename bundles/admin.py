from django.contrib import admin
from .models import Bundle, BundleBill


class BundleBillInline(admin.TabularInline):
    model = BundleBill
    readonly_fields = ("bundle",)
    raw_id_fields = ("bill",)


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ("slug", "name")

    inlines = [BundleBillInline]
