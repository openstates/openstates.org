from django.shortcuts import render
from .models import DataExport


def overview(request):
    return render(request, "bulk/overview.html", {})


def bulk_csv_list(request):
    exports = (
        DataExport.objects.filter(data_type="csv")
        .select_related("session", "session__jurisdiction")
        .order_by("session__jurisdiction__name", "session__name")
    )
    return render(request, "bulk/bulk_csv_list.html", {"exports": exports})
