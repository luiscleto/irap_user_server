from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from django.db import models
from djangotoolbox.fields import BlobField

# Create your models here.


class Experiment(models.Model):
    author = models.CharField(max_length=30, blank=False)
    title = models.CharField(max_length=60, unique=True, blank=False)
    description = models.CharField(max_length=1500, blank=False)
    date_modified = models.DateTimeField(default=datetime.now)
