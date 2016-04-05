from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from mongoengine import Document, ReferenceField, StringField, IntField, DateTimeField, CASCADE


# Create your models here.


class Experiment(Document):
    user = StringField(max_length=60, required=True)
    title = StringField(max_length=200, required=True)
    description = StringField(required=True)
    description_length = IntField()
    date_modified = DateTimeField(default=datetime.now)
