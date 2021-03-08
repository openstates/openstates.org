from django.contrib import admin
from .models import UnmatchedName, DeltaSet


@admin.register(UnmatchedName)
class UnmatchedNameAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "name",
        "sponsorships_count",
        "votes_count",
        "get_status_display",
    )
    list_filter = (
        "session__jurisdiction",
        "status",
    )


@admin.register(DeltaSet)
class DeltaSetAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "get_pr_status_display", "created_at")
    list_filter = ("pr_status",)
