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
    print "requesting experiment to start"
    r = requests.get(IRAP_SERVER_ADDRESS + '/irap/run/' + exp.title)
    print r.text
