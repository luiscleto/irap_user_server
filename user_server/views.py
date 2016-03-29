# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

# Create your views here.


def index(request):
    return HttpResponse(u'Testing <a href="/login">login</a>.')


def profile(request):
    return render(request, 'profile.html', {"foo": "bar"})
