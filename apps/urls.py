from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from apps import views
urlpatterns = [
    path('list/', views.snippet_list),
]

urlpatterns = format_suffix_patterns(urlpatterns)