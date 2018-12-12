from django.shortcuts import render


def committees(request, state):
    return render(request, "public/views/committees.html", {"state": state})


def committee(request, state):
    return render(request, "public/views/committee.html", {"state": state})
