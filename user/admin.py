from django.contrib import admin
from user.models import TecUser, Logs, AppConfiguration
# Register your models here.
admin.site.register(TecUser)
admin.site.register(Logs)
admin.site.register(AppConfiguration)

