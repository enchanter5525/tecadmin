from django.utils import timezone
import requests
from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth.hashers import check_password, make_password
from django.core import serializers
from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework import status
import asyncio
from TecAdminWebConsole.settings import AUTH_URL
from user.serializers import AppConfigSerializer, LogsSerializer, TUserSerializer
from user.models import AppConfiguration, Logs, TecUser
from rest_framework import generics, permissions, viewsets, views
from rest_framework.decorators import action
from rest_framework.response import Response
from fcache.cache import FileCache
my_cache = FileCache('myapp')

class TCreateUserView(viewsets.ModelViewSet):
    queryset = TecUser.objects.all()
    serializer_class = TUserSerializer
    lookup_field = 'userid'
    # permission_classes = [permissions.IsAuthenticated]


    @action(detail=False, methods=['POST'])
    def login(self, request, *args, **kwargs):
        print('Got here in the login', request.data)
        # snippet = self.get_object()
        try:
            zeroin_user = TecUser.objects.get(userid=request.data['userid'])
            required_user = model_to_dict(zeroin_user)
            print('Im here',check_password(request.data["password"], required_user["password"]))
            if check_password(request.data["password"], required_user["password"]):
                return Response({'login': True, 'error': None})
            return Response({'login': False, 'error': 'Invalid password'})
        except:
            print('Exception occured')
            return Response({'login': False, 'error': 'Invalid user'})


    # def create(self, request):
    #     print('This is post')
    #     pass
    #
    # def retrieve(self, request, userid, pk=None):
    #     print('This is retrieve', pk)
    #     return Response('Thsi is retrieb')

    #
    # def update(self, request, pk=None):
    #     pass
    #
    # def partial_update(self, request, pk=None):
    #     pass
    #
    # def destroy(self, request, pk=None):
    #     pass
class ApplicationLogsView(viewsets.ModelViewSet):
    queryset = Logs.objects.all()
    serializer_class = LogsSerializer
    

    def create(self, request, *args, **kwargs):
        print('In the final of create in Logs', args)
        return super().create(request, *args, **kwargs)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class AppConfigurationView(viewsets.ReadOnlyModelViewSet):
    queryset = AppConfiguration.objects.all()
    serializer_class = AppConfigSerializer



class OktaAuthView(viewsets.ModelViewSet):

    # @action(detail=False, methods=['POST'])
    def create(self, request, *args, **kwargs):
        try:
            print('GetClientIP',get_client_ip(request) )
            username = request.data['userid']
            password = request.data['password']
            # print('Request', request.data, args, kwargs)
            post_data = {
                "username": username,
                "password": password,
                "options": {
                    "multiOptionalFactorEnroll": True,
                    "warnBeforePasswordExpired": True
                }
            }
            okta_primary_auth = requests.post(AUTH_URL + '/api/v1/authn', json=post_data)
            p_auth_response = okta_primary_auth.json()
            # print('p_auth_response', p_auth_response)

            if 'errorSummary' in p_auth_response:
                return Response({
                    'login': False,
                    'error': p_auth_response['errorSummary']
                })
            else:
                if p_auth_response['status'] == 'MFA_REQUIRED':
                    return Response({
                    'login': 'Pending',
                    'mfa': p_auth_response
                    });
                else: # MFA is not needed for this.
                    # print(p_auth_response['sessionToken'])
                    params = {
                        'client_id': '0oat2nueceDS6I2G90h7',
                        'response_type': 'token id_token',
                        'response_mode': 'fragment',
                        'scope': 'openid okta.users.read.self okta.users.read okta.users.manage',
                        'redirect_uri': 'http://localhost:4200/login',
                        'state': 'state',
                        'nonce': 'bhan',
                        'sessionToken': p_auth_response['sessionToken']

                    }
                    url = AUTH_URL + '/oauth2/v1/authorize'
                    # print(url)
                    response = requests.get(url, params=params, allow_redirects=False)
                    if response.status_code == 302:
                        # user_instance = TecUser.objects.get(userid=request.data['userid'])
                        # logs = Logs(userid=user_instance, timestamp=timezone.now(), activity='login', ip_address=get_client_ip(request))
                        # logs.save()
                        # print(response.text)
                        # print(response.headers['location'])
                        access_token = response.headers['location'].split('access_token=')
                        # print(access_token[1])
                        my_cache['access_token'] = access_token[1].split('&token_type')[0]
                        return Response({
                            'login': True,
                            'error': None
                        })
                    else:
                        return Response({
                            'login': False,
                            'error': None
                        })

        except Exception as e:
            # print('Common Exceprion', e)
            return Response({
                'login': False,
                'error': 'Login Failed'
            })


class OktaFactorView(viewsets.ModelViewSet):

    @action(detail=True, methods=['POST'])
    def verify(self, request, *args, **kwargs):
        try:
            # print('kwargs.pk', kwargs["pk"])
            pk = kwargs["pk"]
            url = f"{AUTH_URL}/api/v1/authn/factors/{pk}/verify"

            print('url', url)
            
            mfa_response = requests.post(url, json=request.data)
            
            p_auth_response = mfa_response.json()
            # print('p_auth_response', p_auth_response)

            if 'errorSummary' in p_auth_response:
                return Response({
                    'login': False,
                    'error': p_auth_response['errorSummary']
                })
            else:
                if p_auth_response['status'] == 'MFA_REQUIRED' or p_auth_response['status'] == 'MFA_CHALLENGE':
                    return Response({
                    'login': 'Pending',
                    'mfa': p_auth_response
                    });
                else: # MFA is not needed for this.
                    # print(p_auth_response['sessionToken'])
                    params = {
                        'client_id': '0oat2nueceDS6I2G90h7',
                        'response_type': 'token id_token',
                        'response_mode': 'fragment',
                        'scope': 'openid okta.users.read.self okta.users.read okta.users.manage',
                        'redirect_uri': 'http://localhost:4200/login',
                        'state': 'state',
                        'nonce': 'bhan',
                        'sessionToken': p_auth_response['sessionToken']

                    }
                    url = AUTH_URL + '/oauth2/v1/authorize'
                    # print(url)
                    response = requests.get(url, params=params, allow_redirects=False)
                    if response.status_code == 302:
                        # user_instance = TecUser.objects.get(userid=request.data['userid'])
                        # logs = Logs(userid=user_instance, timestamp=timezone.now(), activity='login', ip_address=get_client_ip(request))
                        # logs.save()
                        # print(response.text)
                        # print(response.headers['location'])
                        access_token = response.headers['location'].split('access_token=')
                        # print(access_token[1])
                        my_cache['access_token'] = access_token[1].split('&token_type')[0]
                        return Response({
                            'login': True,
                            'error': None
                        })
                    else:
                        return Response({
                            'login': False,
                            'error': None
                        })
        except Exception as e:
            return Response({
                'error': e
            })


