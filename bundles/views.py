from .models import Bundle
from django.shortcuts import render_to_response


def bundle_view(request, slug):
    bundle = Bundle.objects.get(slug=slug)
    bills = bundle.bills.all().order_by("order")

    return render_to_response("bundles/bundle.html", {"bundle": bundle, "bills": bills})
