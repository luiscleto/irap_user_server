# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required

from user_server.forms import *
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext


# Create your views here.


def index(request):
    return render(request, 'index.html')


def profile(request, username):
    try:
        u = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'profile.html', {'selected_user': u})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/accounts/profile/'+form.cleaned_data['username'])
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})

    return render_to_response('registration/register.html', variables, )


def experiments_index(request):
    exps = Experiment.objects.only('author', 'status', 'title').order_by('-date_created')
    return render(request, 'experiments/list.html', {'experiments': exps})


def user_experiments(request, username):
    try:
        User.objects.get(username__iexact=username)
        exps = Experiment.objects.only('author', 'status', 'title').filter(author__iexact=username).order_by('-date_created')
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'experiments/list_by_user.html', {'username': username, 'experiments': exps})


@login_required
def create_experiment(request):
    if request.method == 'POST':
        form = ExperimentForm(request.POST)
        if form.is_valid():
            exp = Experiment.objects.create(
                author=request.user.get_username(),
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
            )
            return HttpResponseRedirect('/experiments/'+exp.title)
    else:
        form = ExperimentForm()
    return render(request, 'experiments/create.html', {'form': form})


def view_experiment(request, exp_title):
    try:
        e = Experiment.objects.get(title__iexact=exp_title)
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")
    return render(request, 'experiments/view.html', {'experiment': e})


def page_not_found_view(request):
    return render(request, '404.html')


def not_yet_done(request):
    return render(request, 'todo.html', )


@login_required
def redirect_to_user_profile(request):
    return HttpResponseRedirect('/accounts/profile/' + request.user.get_username())
