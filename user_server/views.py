# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required

from user_server.forms import *
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core import serializers

from utils import *


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
            return HttpResponseRedirect('/accounts/profile/' + form.cleaned_data['username'])
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})

    return render_to_response('registration/register.html', variables, )


def experiments_index(request):
    experiments = Experiment.objects.only('author', 'status', 'title').order_by('-date_created')
    return render(request, 'experiments/list.html', {'experiments': experiments})


def user_experiments(request, username):
    try:
        User.objects.get(username__iexact=username)
        experiments = Experiment.objects.only('author', 'status', 'title').filter(author__iexact=username).order_by(
            '-date_created')
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'experiments/list_by_user.html', {'username': username, 'experiments': experiments})


def get_user_unfinished_experiments(request, username):
    try:
        User.objects.get(username__iexact=username)
        experiments = Experiment.objects.only('author', 'status', 'title').filter(author__iexact=username,
                                                                                  status__lt=100,
                                                                                  status__gt=-0.5).order_by(
            '-date_created')
    except User.DoesNotExist:
        raise Http404("User does not exist")
    data = serializers.serialize('json', experiments)
    return HttpResponse(data, mimetype='application/json')


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
            return HttpResponseRedirect('/experiments/' + exp.title)
    else:
        form = ExperimentForm()
    return render(request, 'experiments/create.html', {'form': form})


def view_experiment(request, exp_title):
    try:
        e = Experiment.objects.get(title__iexact=exp_title)
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")
    return render(request, 'experiments/view.html', {'experiment': e})


@login_required
def create_reference_genome(request):
    if request.method == 'POST':
        ss = ''
        form = ReferenceGenomeForm(request.POST)
        if form.is_valid():
            s, created = Species.objects.get_or_create(name__iexact=form.cleaned_data['species'].lower())
            if created:
                s.name = form.cleaned_data['species'].lower()
                s.save()
            version_no = get_next_version_number(s)
            rg = ReferenceGenome.objects.create(
                species=s,
                version=version_no,
                file_name=s.name+"."+str(version_no)+".gtf.gz"
            )
            return HttpResponseRedirect('/reference-genomes/' + s.name)
    else:
        ss = Species.objects.all()
        form = ReferenceGenomeForm()
    return render(request, 'ReferenceGenomes/create.html', {'form': form, 'species': ss})


def view_reference_genome(request, species):
    try:
        s = Species.objects.get(name__iexact=species)
        rgs = ReferenceGenome.objects.only('version', 'date_created').filter(species__exact=s).order_by('-version')
    except Species.DoesNotExist:
        raise Http404("No reference genomes exist for that species")
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")
    return render(request, 'ReferenceGenomes/view.html', {'reference_genomes': rgs, 'species': s})


def list_reference_genome(request):
    try:
        ss = Species.objects.all()
        e = ReferenceGenome.objects.all()
    except Experiment.DoesNotExist:
        raise Http404("No reference genomes exist")
    return render(request, 'ReferenceGenomes/list.html', {'reference_genomes': e, 'species': ss})


def page_not_found_view(request):
    return render(request, '404.html')


def not_yet_done(request):
    return render(request, 'todo.html', )


@login_required
def redirect_to_user_profile(request):
    return HttpResponseRedirect('/accounts/profile/' + request.user.get_username())
