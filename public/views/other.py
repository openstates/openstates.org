from django.shortcuts import render


def styleguide(request):
    return render(request, 'public/views/styleguide.html')


def home(request):
    return render(request, 'public/views/home.html')


def jurisdiction(request, state):
    return render(
        request,
        'public/views/jurisdiction.html',
        {'state': state}
    )
