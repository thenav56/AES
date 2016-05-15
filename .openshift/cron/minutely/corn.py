import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()


def train_scheduled_job():
    from django.conf import settings
    os.chdir(settings.BASE_DIR)
    from essay.models import CronJob
    try:
        cronjob = CronJob.objects.order_by('updated').filter(status='0')[0]
        print("Train Job(pk=%s) for essayModel( %s )" % (cronjob.pk,
              cronjob.essaymodel))
        if cronjob is not None:
            cronjob.train()
    except IndexError:
        print("Empty queue")

if __name__ == "__main__":
    import fcntl
    try:
        f = open('corn.lock', 'w')
        fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        train_scheduled_job()
    except IOError:
        print("Another Instance is already working")
