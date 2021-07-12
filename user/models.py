from django.db import models


class TecUser(models.Model):
    uid = models.UUIDField()
    userid = models.CharField(max_length=100, primary_key=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=60)
    password = models.CharField(max_length=150,)
    dob = models.DateTimeField(max_length=40)
    identity = models.CharField(max_length=20)
    remarks = models.CharField(max_length=50)

    # def __str__(self):
    #     return self.userid