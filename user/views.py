import requests
from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth.hashers import check_password
from django.core import serializers
from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework import status
import asyncio
from TecAdminWebConsole.settings import AUTH_URL
from user.serializers import TUserSerializer
from user.models import TecUser
from rest_framework import generics, permissions, viewsets, views
from rest_framework.decorators import action
from rest_framework.response import Response

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

class OktaAuthView(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        userid = request.query_params.get('id')
        print('username', userid)
        try:
            token = "eyJraWQiOiJPbU1kanNuWjFKWDltYjlFUDBCUTRIRjBwVnJVMWlZVi1MM2NySllBMlVzIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULk45NXVPNEZZM2ZxV2hPVGRPRkJONFZZaEdiSTZ2dlJwbzcwZ0JlUzA0MEUiLCJpc3MiOiJodHRwczovL3RlY25pY3MtZGV2Lm9rdGFwcmV2aWV3LmNvbSIsImF1ZCI6Imh0dHBzOi8vdGVjbmljcy1kZXYub2t0YXByZXZpZXcuY29tIiwic3ViIjoidGVzdHdjMkB0ZWNuaWNzLmNvbSIsImlhdCI6MTYyNTgyMjYwMCwiZXhwIjoxNjI1ODI2MjAwLCJjaWQiOiIwb2F0Mm51ZWNlRFM2STJHOTBoNyIsInVpZCI6IjAwdXRldm5maGxodjlqTnRIMGg3Iiwic2NwIjpbIm9wZW5pZCIsIm9rdGEudXNlcnMucmVhZC5zZWxmIiwib2t0YS51c2Vycy5yZWFkIiwib2t0YS51c2Vycy5tYW5hZ2UiXX0.fBlwX_GY-kLsZgVcTlAeM_y1X9sx6LBuxsa2oqNcPT4Au3mWBlBAA4L2wHvWQkIhzJFotkeZ0Ce_QoM9Hx64fGWqsT8ABjzmDipmS-YaTtjmqWxaebFn-Ud1JpdouRxuGJhNAJ6io2I_1VhrVkANh_K8bSL8NGyd7SuBwWpZJogJnvpyTgBiW0eVGWLSkPTKMVFub30KYLUUx8DiyTwt6mVoB6IyWnDjk9cgPRjxqxNLTUz0zkvtbqRFg5Hzem_-Ld22bVjhICSvGsPfKzfcF9feL62oSEnSS0HK4Yi71MmIkitIaycZEjaytkEumV05biTxN_6NH9RHgDPLNX1rig"
            if userid is not None:
                print('username is not nine')
                url = f"{AUTH_URL}/api/v1/users/{userid}"
            else:
                url = f"{AUTH_URL}/api/v1/users"
            response = requests.get(url,
                                     headers={'AUTHORIZATION': 'Bearer' + token})
            json_response = response.json()
            return Response(json_response)
        except Exception as e:
            print('Unkown error', e)
            return Response('Cant Fetch the users ATM')

    @action(detail=False, methods=['POST'])
    def login(self, request, *args, **kwargs):
        try:
            username = request.data['userid']
            password = request.data['password']
            print('Request', request.data, args, kwargs)
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
            print('p_auth_response', p_auth_response)

            if 'errorSummary' in p_auth_response:
                return Response({
                    'login': False,
                    'error': p_auth_response['errorSummary']
                })
            else:
                print(p_auth_response['sessionToken'])
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
                print(url)
                response = requests.get(url, params=params, allow_redirects=False)
                print(response.text)
                print(response.headers['location'])
                access_token = response.headers['location'].split('access_token=')
                print(access_token[1])
                return Response({
                    'login': True,
                    'error': access_token[1].split('&token_type')[0]
                })
        except Exception as e:
            print('Common Exceprion', e)
            return Response({
                'login': False,
                'error': 'Login Failed'
            })

    @async_to_sync
    async def create(self, request, *args, **kwargs):
        token = "eyJraWQiOiJPbU1kanNuWjFKWDltYjlFUDBCUTRIRjBwVnJVMWlZVi1MM2NySllBMlVzIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULkQ0R0VVWGs4RWNyS0U5eGc3VnlNand6VTNKdWhYMHpYMTdzTzRUZjg2eFkiLCJpc3MiOiJodHRwczovL3RlY25pY3MtZGV2Lm9rdGFwcmV2aWV3LmNvbSIsImF1ZCI6Imh0dHBzOi8vdGVjbmljcy1kZXYub2t0YXByZXZpZXcuY29tIiwic3ViIjoidGVzdHdjMkB0ZWNuaWNzLmNvbSIsImlhdCI6MTYyNjA4MDYzNywiZXhwIjoxNjI2MDg0MjM3LCJjaWQiOiIwb2F0Mm51ZWNlRFM2STJHOTBoNyIsInVpZCI6IjAwdXRldm5maGxodjlqTnRIMGg3Iiwic2NwIjpbIm9wZW5pZCIsIm9rdGEudXNlcnMucmVhZC5zZWxmIiwib2t0YS51c2Vycy5yZWFkIiwib2t0YS51c2Vycy5tYW5hZ2UiXX0.Iwslx0p3R4nDKqXqQ7F9sWZdm2SreSghK84YtxBn7EBB5aIAltf9AudXV23vOM0h00oSAgbphhh0m4tr_N2tCUUL5Rk_mOe-aUmFk7FAjcooyq0Hangm3K4B57NBgFBRJilYEZsnpuJTEdpXUzalzIg9DahoJpL9It8GUGkwrk7KZiKSzDY0U3CbBC7-W1PWSooegwHv38yaQAnZDDYMEJuVY8wMi8AXHFKbRmRjHBqTHyaonAfqFdJHnHwwtXYuMS8fbZQ2KD15XTmKSkmIZa1Hd4xdgDLq4Z5CuKMvTD9hMkTGPKiUUQokmo_r3HNOy-BV8tsZa9_hB9CBi3lScw"
        # config = {
        #     'orgUrl': AUTH_URL,
        #     'authorizationMode': 'PrivateKey',
        #     'clientId': '0oa107ievucoFEIUJ0h8',
        #     'scopes': [ 'okta.users.read'],
        #     'privateKey': """{
        #         "p": "4cahiOt4d8_LHJ4Uy7gBINPPDs5yQExXjoVgSRlfVvLsRPWD8S390I2nZ1bLXOfvnnnMh4zAhXUU1_JdMfXEyx0eRYVVFSwYrCXm7i42aQHd6RnL1vx4ri8nx5eq-1HIQYfZnaT9IwEfjtwKaZB-6wkdws_wmb2VzOaPyY1Ehm0",
        #         "kty": "RSA",
        #         "q": "zPsMIHsQq93UsnjBBUv_7qxMIeKMCGVxMdeMPyYgxbS63qRxVKEo30oCyhrzI5tcylNWkml1KiK3y1DaEwmeUR8T9nzE7oczcO9EVh6tI6AQEIrDQ_OYW7sNqcKezNGGv2S7iZ0Gn-AFOcL-wDCLAnQko65h-lB905Dh2A2XHNk",
        #         "d": "ezvBX2849y4bGiRj2xcsLvngp1TjcmhvDpuLZJ4IfMVZyB2WSzrZmIab_fN2rOSo9cQiM_Q7gq7V2PBdVcM0tLxJ7omo2VX9Jglj8tRJjIJfs2gQmHeDtCVFzQ_f73nNcg0y6zXu-HpOmgsXt6Ev3x-bIvHjzilKZ6RKee9Ksk3ribUYur8NtttsowTH0cq256rMTB3wtCyAViHCO-0pBM0-RilH5CaId9P5nE33K4sM82VtJUlfA53MH4sBR82LvjC2qqjK3aDs3SIYvB-34MHuedlUDHLjh90hIFM5kg1MQjjWhMVhXgCEfMIpD-3Wh0eQbxD5iMsSrdOiZBgBYQ",
        #         "e": "AQAB",
        #         "use": "sig",
        #         "qi": "SBobT6XENUsx9We-anQ6_3MI8bRKBMrlAMbaC4XqZiO8thSTvS7NSqfiVTbkFgoAmG9Yf4qUFX_Mylh7CX6lBoxnEDz80_0e5ryHoEXC3YNC6xvs7r7UHwLBaY40zXYslmVziQCCxg316lJrmCvyQXhjSZziPG6XiaMsoo16M9c",
        #         "dp": "bR_QW5lUNLSee0p8yqo5AWDep01pM2KyvxQAIdS9nAz13a69AwkzsGWHEA-HY3RHANXl4W5KbzbTyDxAhzE-2N1OEFQNd5pEoo__OgfkDIT2eQAa4eJNggMQuwu3fJlerS24JNXl89FLK4V3EubgMUHKvKo8pFJZ4RtfTA-Xm1E",
        #         "alg": "RS256",
        #         "dq": "DjMl9-oOkZlgbqym0nMdW69b5s0G3l4IpWdFM-q0Qn3upBXINBCmADHkV5PeXA0bNHjpemML1sto6BDFyqPT79KzU1P5YHzFN4GbvkuJuvoPotW6CS8K0u_2VlhBH_cz2nZj93iFSPX_5qx3cWDrgFQDZcNizjBdRxa2Tn1ChqE",
        #         "n": "tMexK3HSnlhW6xB8aaki52loAXPvAu1vw3UWMbxJNABV5MztrGy-DuNwA0wqJ2i1XZlNRfOzI6xFs6aqpfaa45PrXUID1WINsgxmdWRJpmmWVR28AfLsq3pzLjCcIoGW9pa_A-stXnKuMN2z87JRSpxkYtd2bYjkzcFVmxmZyuP1dF0IldCgjr0mmUgVO2tAk6CnYFdO-EMSoWPK885HPfiPm6D4HWf7LjBS_a5FVtmZtjZjC0V8anLq12PbE_95tLNmUpvfB28JZkfjheP3uP4rlizF7BEEBFqjT9OlVu0ZEZtCpXaIoLBb2FM242t7hUJmErFzw3jTf_SDERTeZQ"
        #     }"""
        # }
        # okta_client = OktaClient(config)
        # print('CAME HERE', okta_client)
        # users, resp, err = await okta_client.list_users()
        # # for user in users:
        # print(users, err)
        try:
            create_user_body = {
            "profile": {
                "firstName": request.data['firstname'],
                "lastName": request.data['lastname'],
                "email": request.data['email'],
                "login": request.data['email']
            },
            "credentials": {
                "password" : { "value": request.data['password'] }
            }
            }
            print(create_user_body)
            # create_user_body = request.data
            response = requests.post(AUTH_URL+'/api/v1/users?activate=true', json=create_user_body,
                                    headers={'AUTHORIZATION': 'Bearer'+token})
            json_response = response.json()
            print(json_response)
            if 'errorSummary' in json_response:
                return Response({
                    'created': False,
                    'uid': None,
                    'error': json_response['errorSummary']
                })
            else:
                return Response({
                    'created': True,
                    'uid': json_response['id'],
                    'error': False
                })
        except Exception as e:
            print('Exception occured in the create()', e)
            return Response({
                 'created': False,
                    'uid': None,
                    'error': e
            })

    @action(detail=False, methods=['POST'])
    def reset_password(self, request, *args, **kwargs):
        try:
            token = "eyJraWQiOiJPbU1kanNuWjFKWDltYjlFUDBCUTRIRjBwVnJVMWlZVi1MM2NySllBMlVzIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULkQ0R0VVWGs4RWNyS0U5eGc3VnlNand6VTNKdWhYMHpYMTdzTzRUZjg2eFkiLCJpc3MiOiJodHRwczovL3RlY25pY3MtZGV2Lm9rdGFwcmV2aWV3LmNvbSIsImF1ZCI6Imh0dHBzOi8vdGVjbmljcy1kZXYub2t0YXByZXZpZXcuY29tIiwic3ViIjoidGVzdHdjMkB0ZWNuaWNzLmNvbSIsImlhdCI6MTYyNjA4MDYzNywiZXhwIjoxNjI2MDg0MjM3LCJjaWQiOiIwb2F0Mm51ZWNlRFM2STJHOTBoNyIsInVpZCI6IjAwdXRldm5maGxodjlqTnRIMGg3Iiwic2NwIjpbIm9wZW5pZCIsIm9rdGEudXNlcnMucmVhZC5zZWxmIiwib2t0YS51c2Vycy5yZWFkIiwib2t0YS51c2Vycy5tYW5hZ2UiXX0.Iwslx0p3R4nDKqXqQ7F9sWZdm2SreSghK84YtxBn7EBB5aIAltf9AudXV23vOM0h00oSAgbphhh0m4tr_N2tCUUL5Rk_mOe-aUmFk7FAjcooyq0Hangm3K4B57NBgFBRJilYEZsnpuJTEdpXUzalzIg9DahoJpL9It8GUGkwrk7KZiKSzDY0U3CbBC7-W1PWSooegwHv38yaQAnZDDYMEJuVY8wMi8AXHFKbRmRjHBqTHyaonAfqFdJHnHwwtXYuMS8fbZQ2KD15XTmKSkmIZa1Hd4xdgDLq4Z5CuKMvTD9hMkTGPKiUUQokmo_r3HNOy-BV8tsZa9_hB9CBi3lScw"
            userid = request.query_params.get('id')
            print(userid)
            url = f"{AUTH_URL}/api/v1/users/{userid}/lifecycle/reset_password?sendEmail=true"
            response = requests.post(url,
                                     headers={'AUTHORIZATION': 'Bearer' + token})
            if response.status_code == 401:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                json_response = response.json()
                return Response(json_response)
        except Exception as e:
            print('Exception occured in the reset password', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['delete'], detail=False)
    def delete(self, request):
        try:
            userid = request.query_params.get('id')
            print('username', userid)
            token = "eyJraWQiOiJPbU1kanNuWjFKWDltYjlFUDBCUTRIRjBwVnJVMWlZVi1MM2NySllBMlVzIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULk45NXVPNEZZM2ZxV2hPVGRPRkJONFZZaEdiSTZ2dlJwbzcwZ0JlUzA0MEUiLCJpc3MiOiJodHRwczovL3RlY25pY3MtZGV2Lm9rdGFwcmV2aWV3LmNvbSIsImF1ZCI6Imh0dHBzOi8vdGVjbmljcy1kZXYub2t0YXByZXZpZXcuY29tIiwic3ViIjoidGVzdHdjMkB0ZWNuaWNzLmNvbSIsImlhdCI6MTYyNTgyMjYwMCwiZXhwIjoxNjI1ODI2MjAwLCJjaWQiOiIwb2F0Mm51ZWNlRFM2STJHOTBoNyIsInVpZCI6IjAwdXRldm5maGxodjlqTnRIMGg3Iiwic2NwIjpbIm9wZW5pZCIsIm9rdGEudXNlcnMucmVhZC5zZWxmIiwib2t0YS51c2Vycy5yZWFkIiwib2t0YS51c2Vycy5tYW5hZ2UiXX0.fBlwX_GY-kLsZgVcTlAeM_y1X9sx6LBuxsa2oqNcPT4Au3mWBlBAA4L2wHvWQkIhzJFotkeZ0Ce_QoM9Hx64fGWqsT8ABjzmDipmS-YaTtjmqWxaebFn-Ud1JpdouRxuGJhNAJ6io2I_1VhrVkANh_K8bSL8NGyd7SuBwWpZJogJnvpyTgBiW0eVGWLSkPTKMVFub30KYLUUx8DiyTwt6mVoB6IyWnDjk9cgPRjxqxNLTUz0zkvtbqRFg5Hzem_-Ld22bVjhICSvGsPfKzfcF9feL62oSEnSS0HK4Yi71MmIkitIaycZEjaytkEumV05biTxN_6NH9RHgDPLNX1rig"
            if userid is not None:
                print('username is not nine')
                url = f"{AUTH_URL}/api/v1/users/{userid}"
                response = requests.delete(url,
                                        headers={'AUTHORIZATION': 'Bearer' + token})
                if response.status_code == 204:
                    return Response(status=response.status_code)

                return Response(data=response.json(), status=response.status_code)
            else:
                print('Enter the userid')
                return Response({
                    'error': 'Enter the userid'
                })
        except Exception as e:
            print('Unkown error', e)
            return Response({'error': 'Cannot delete the user'})
