from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django import forms
from .templatetags.timedelta import timeDelta

from .models import EssayModel, CronJob, Essay


class MyAdminSite(AdminSite):
    site_header = 'AEGS administration'

    def __init__(self, *args, **kwargs):
        super(MyAdminSite, self).__init__(*args, **kwargs)
        self._registry.update(admin.site._registry)  # PART 2

admin_site = MyAdminSite(name='aegs')


# Model Field Widget Change
# --------------------------------
class EssayModelForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    class Meta:
        fields = '__all__'
        model = Essay


class EssayModelModelForm(forms.ModelForm):
    info = forms.CharField(widget=forms.Textarea)
    class Meta:
        fields = '__all__'
        model = EssayModel


class CronJobAdmin(admin.ModelAdmin):
    list_display = ('essaymodel', 'get_status_display', 'train_time_')

    def train_time_(self, obj):
        return timeDelta(obj.train_time)

class EssayAdmin(admin.ModelAdmin):
    list_display = ('user', 'essaymodel', 'predicted_mark', 'original_mark')
    form = EssayModelForm


class EssayModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'train_len', 'cron_status', 'train_time')
    form = EssayModelModelForm

    def cron_status(self, obj):
        return obj.cronjob.get_status_display()

    def train_time(self, obj):
        return timeDelta(obj.cronjob.train_time)


# --------------------------------
# Model Field Widget Change
admin_site.register(EssayModel, EssayModelAdmin)
admin_site.register(CronJob, CronJobAdmin)
admin_site.register(Essay, EssayAdmin)
