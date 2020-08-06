import stripe
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse


@require_POST
def custom_donation(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # round to nearest dollar
    try:
        amount = int(float(request.POST["dollars"]))
    except ValueError:
        return JsonResponse({"error": "invalid dollar amount"})
    if amount < 5:
        return JsonResponse(
            {"error": "can not donate less than $5 due to merchant fees"}
        )

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
    success = "success" in request.GET
    return render(
        request,
        "flat/donate.html",
        {"success": success, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY},
    )
