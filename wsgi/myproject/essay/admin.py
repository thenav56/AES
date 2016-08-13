from django.contrib import admin

from .models import EssayModel, CronJob, Essay


admin.site.register(EssayModel)
admin.site.register(CronJob)
admin.site.register(Essay)
