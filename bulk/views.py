from django.shortcuts import render
from .models import DataExport


def bulk_csv_list(request):
    exports = (
        DataExport.objects.all()
        .select_related("session", "session__jurisdiction")
        .order_by("session__jurisdiction__name", "session__name")
    )
    return render(request, "bulk/bulk_csv_list.html", {"exports": exports})
