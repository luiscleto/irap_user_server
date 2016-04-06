# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required

from user_server.forms import *
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext


# Create your views here.


def index(request):
    return render(request, 'index.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/accounts/profile/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})

    return render_to_response('registration/register.html', variables, )


def experiments_index(request):
    return render(request, 'experiments/list.html', )


def user_experiments(request, username):
    return render(request, 'experiments/list_by_user.html', {'username': username})


@login_required
def create_experiment(request):
    if request.method == 'POST':
        form = ExperimentForm(request.POST)
        if form.is_valid():
            Experiment.objects.create(
                author=request.user.get_username(),
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
            )
            return HttpResponseRedirect('/experiments/list/')
    else:
        return render(request, 'experiments/create.html', )


def not_yet_done(request):
    return render(request, 'todo.html', )
