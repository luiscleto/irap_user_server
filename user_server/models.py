from django.contrib.auth.models import User
from django.core.validators import *
from django.utils.datetime_safe import datetime
from django.db import models

# Create your models here.
from user_server import gridfs_storage


class RefGenome(models.Model):
    file_address = models.URLField(unique=True, blank=False)
    file_content = models.FileField(storage=gridfs_storage, upload_to='/')
    date_created = models.DateTimeField(default=datetime.now)


class GTFFile(models.Model):
    file_address = models.URLField(unique=True, blank=False)
    file_content = models.FileField(storage=gridfs_storage, upload_to='/')
    date_created = models.DateTimeField(default=datetime.now)


class Experiment(models.Model):
    author = models.CharField(max_length=30, blank=False)
    title = models.CharField(max_length=60, unique=True, blank=False, validators=[
            RegexValidator(
                r'^\w+$',
                'Invalid character used in title'
            ),
            MinLengthValidator(4),
            MaxLengthValidator(60),
        ],)
    description = models.CharField(max_length=1500, blank=False)
    status = models.FloatField(default=5)
    conf_file = models.FileField(storage=gridfs_storage, upload_to='/')
    libraries_file = models.FileField(storage=gridfs_storage, upload_to='/')  # compressed file with all libraries
    reference_genome = models.ForeignKey(RefGenome)
    gtf_file = models.ForeignKey(GTFFile)
    date_created = models.DateTimeField(default=datetime.now)
    date_modified = models.DateTimeField(default=datetime.now)


class Species(models.Model):
    name = models.CharField(max_length=80, unique=True, blank=False, validators=[
        MinLengthValidator(8),
        MaxLengthValidator(80)
    ])
    date_created = models.DateTimeField(default=datetime.now)


class ReferenceGenome(models.Model):
    species = models.ForeignKey(Species)
    version = models.BigIntegerField(blank=False)
    file_name = models.CharField(max_length=120, unique=True, blank=False)
    date_created = models.DateTimeField(default=datetime.now)
