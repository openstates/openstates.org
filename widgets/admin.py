from django.contrib import admin
from .models import WidgetConfig


@admin.register(WidgetConfig)
class WidgetAdmin(admin.ModelAdmin):
    pass
