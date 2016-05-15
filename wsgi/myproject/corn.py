import os


def train_scheduled_job():
    import django
    import sys

    on_openshift = False
    if 'OPENSHIFT_APP_NAME' in os.environ:
        on_openshift = True

    if on_openshift:
        sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR'],
                        'wsgi/myproject'))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    django.setup()

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
        lock_file = os.path.join(os.environ['OPENSHIFT_TMP_DIR'], 'corn.lock')
        f = open(lock_file, 'w')
        fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        train_scheduled_job()
    except IOError:
        print("Another Instance is already working")
