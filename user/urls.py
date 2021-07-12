from django.urls import path, include
from rest_framework.routers import DefaultRouter

from TecAdminWebConsole.settings import AUTHENTICATION_TO_BE_USED
from user import views

app_name = 'user'
router = DefaultRouter()
if AUTHENTICATION_TO_BE_USED == 'local':
    router.register(r'users', views.TCreateUserView)
else:
    router.register(r'users', views.OktaAuthView, basename='okta')
    # router.register(r'^users/(?P<username>.+)/$', views.OktaAuthView, basename='okta')

urlpatterns = [
    path('', include(router.urls)),
]