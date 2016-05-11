import requests

from user_server.models import *
from irap_user_server.local_settings import IRAP_SERVER_ADDRESS


def get_next_version_number(species):
    try:
        rg = ReferenceGenome.objects.only('version').filter(species__exact=species).order_by('-version').last()
        return rg.version+1
    except ReferenceGenome.DoesNotExist:
        return 1


def start_experiment(exp):
    r = requests.get(IRAP_SERVER_ADDRESS + '/irap/run/' + exp.title)
    print(r.text)
    if r.status_code == 404:
        exp.status = -1.0
        exp.fail_message = "Experiment not found by cluster server"
        exp.save()
    elif r.status_code != 200:
        exp.status = -1.0
        exp.fail_message = "Cluster server unknown error"
        exp.save()
