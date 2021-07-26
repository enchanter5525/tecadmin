from django.db import models
from django.db.models.fields.related import ForeignKey
import uuid


class TecUser(models.Model):
    uid = models.UUIDField(default=uuid.uuid4)
    userid = models.CharField(max_length=100, primary_key=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=60)
    password = models.CharField(max_length=150,)
    dob = models.DateTimeField(max_length=40, null=True)
    identity = models.CharField(max_length=20, null=True)
    remarks = models.CharField(max_length=50, null=True)

    # def __str__(self):
    #     return self.userid

class Logs(models.Model):
    uid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    userid = models.ForeignKey(TecUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(max_length=20)
    activity = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    device_env = models.CharField(max_length=150)

class AppConfiguration(models.Model):
    title = models.CharField(unique=True, max_length=100)
    configuration = models.JSONField()