from django.contrib.auth.hashers import make_password
from django.db.models import fields
from user import models

from user.models import AppConfiguration, Logs, TecUser
from rest_framework import serializers


class TUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = TecUser
        fields = ('uid', 'userid', 'phone', 'firstname', 'lastname', 'email', 'password', 'dob', 'identity', 'remarks')
        write_only_fields = ('password',)

    def create(self, validated_data):
        print('--------Create in the serializer', validated_data)
        validated_data['password'] = make_password(validated_data['password'])
        return TecUser.objects.create(**validated_data)

class AppConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppConfiguration
        fields = ('title', 'configuration')

class LogsSerializer(serializers.ModelSerializer):

    class Mets:
        model = Logs
        fields = ('userid', 'timestamp', 'activity', 'ip_address', 'device_env')

    def create(self, validated_data):
        return Logs.objects.create(validated_data)
