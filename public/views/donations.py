import stripe
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse


def donate(request):
    success = False

    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY

        metadata = {
            "source": request.POST.get("source", ""),
            "donor_name": request.POST.get("donor_name", ""),
        }

        customer = stripe.Customer.create(
            source=request.POST["stripeToken"], email=request.POST["email"]
        )
        if "plan" in request.POST:
            stripe.Subscription.create(
                customer=customer, plan=request.POST["plan"], metadata=metadata
            )
        else:
            # just create a one-time charge
            stripe.Charge.create(
                customer=customer,
                amount=request.POST["amount"],
                currency="usd",
                description="Open States Donation",
                metadata=metadata,
                receipt_email=request.POST["email"],
            )
        return JsonResponse({"success": "OK"})

    return render(
        request,
        "flat/donate.html",
        {"success": success, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY},
    )
