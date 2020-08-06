import stripe
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse


@require_POST
def custom_donation(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    amount = int(request.POST["dollars"])
    if amount < 5:
        messages.error(request, "can not donate less than $5 due to merchant fees")
        return redirect("/donate/")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "One-Time Donation"},
                    "unit_amount": amount * 100,  # convert to cents
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="https://openstates.org/donate?success",
        cancel_url="https://openstates.org/donate/",
    )
    return JsonResponse({"session_id": session.id})


def donate(request):
    success = False
    return render(
        request,
        "flat/donate.html",
        {"success": success, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY},
    )
