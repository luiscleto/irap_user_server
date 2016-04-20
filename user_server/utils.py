from user_server.models import *


def get_next_version_number(species):
    try:
        rg = ReferenceGenome.objects.get(species__exact=species).last()
        return rg.version+1
    except ReferenceGenome.DoesNotExist:
        return 1
