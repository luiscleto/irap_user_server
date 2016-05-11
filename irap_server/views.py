from django.http import HttpResponse
from django.shortcuts import render
from django.http import Http404, HttpResponse


# Create your views here.
from user_server.models import Experiment


def run_experiment(request, exp_title):
    try:
        e = Experiment.objects.get(title__iexact=exp_title)
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")
    return HttpResponse('Starting experiment')
