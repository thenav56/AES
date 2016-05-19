from django.contrib import admin

from .models import EssayModel, CronJob


admin.site.register(EssayModel)
admin.site.register(CronJob)
