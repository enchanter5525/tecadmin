from django.contrib.auth.hashers import make_password

from user.models import TecUser
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
