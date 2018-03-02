from django.shortcuts import render


def bills(request, state):
    return render(
        request,
        'public/views/bills.html',
        {
            'state': state
        }
    )


def bill(request, state):
    return render(
        request,
        'public/views/bill.html',
        {
            'state': state
        }
    )
