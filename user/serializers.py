from django.contrib.auth.hashers import make_password
from django.db.models import fields
from user import models, views

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

    class Meta:
        model = Logs
        fields = ('userid', 'timestamp', 'activity')

    def create(self, validated_data):
        print('In the final of create in Logs', validated_data)
        validated_data['ip_address'] = views.get_client_ip(self._context['request'])
        validated_data['device_env'] = 'Nothiung';
        return Logs.objects.create(**validated_data)
