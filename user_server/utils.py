from user_server.models import *


def get_next_version_number(species):
    try:
        rg = ReferenceGenome.objects.only('version').filter(species__exact=species).order_by('-version').last()
        return rg.version+1
    except ReferenceGenome.DoesNotExist:
        return 1
