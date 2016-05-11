from django.http import HttpResponse
from django.shortcuts import render
from multiprocessing import Pool
from django.http import Http404, HttpResponse
from experiment_handler import *


# Create your views here.
from irap_user_server.local_settings import MAX_NUMBER_OF_PROCESSES
from user_server.models import Experiment

pool = Pool(processes=MAX_NUMBER_OF_PROCESSES)


def run_experiment(request, exp_title):
    try:
        e = Experiment.objects.get(title__iexact=exp_title)
        pool.apply_async(start_exp, [e])
    except Experiment.DoesNotExist:
        raise Http404("Experiment does not exist")
    return HttpResponse('Starting experiment')
