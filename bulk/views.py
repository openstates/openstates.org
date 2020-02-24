from django.shortcuts import render
from django.contrib import messages
from .models import DataExport


def overview(request):
    return render(request, "bulk/overview.html", {})


def bulk_session_list(request, data_type):
    if request.user.is_anonymous:
        messages.warning(request, "Please log in to access download links.")
    exports = (
        DataExport.objects.filter(data_type=data_type)
        .select_related("session", "session__jurisdiction")
        .order_by("session__jurisdiction__name", "session__name")
    )
    return render(
        request,
        "bulk/bulk_session_list.html",
        {"exports": exports, "data_type": data_type},
    )
