import os
import time
import datetime


def train_scheduled_job(on_openshift):
    import django
    import sys

    if on_openshift:
        sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR'],
                        'wsgi/myproject'))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    django.setup()

    from essay.models import CronJob
    try:
        cronjob = CronJob.objects.order_by('updated').filter(status='0')[0]
        if cronjob is not None:
            start_t = time.time()
            start_time = datetime.datetime.now()
            print("Train Job(pk=%s) for essayModel( %s )" % (cronjob.pk,
                  cronjob.essaymodel))
            cronjob.train()
            end_t = time.time()
            end_time = datetime.datetime.now()
            total_time = end_time - start_time
            print("Total Time To Train: ", (end_t-start_t))
            print("Started At :", start_time)
            print("AND Ended At :", end_time)
            cronjob.train_time = total_time
            cronjob.save()
            return True
    except IndexError:
        print("Empty queue")
        return False

if __name__ == "__main__":
    import fcntl

    on_openshift = False
    if 'OPENSHIFT_APP_NAME' in os.environ:
        on_openshift = True

    if not on_openshift:
        while 1:
            if not train_scheduled_job(on_openshift):
                exit()
                time.sleep(5*60)
    else:
        try:
            lock_file = os.path.join(os.environ['OPENSHIFT_TMP_DIR'], 'corn.lock')
            f = open(lock_file, 'w')
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            print("Starting Train Scheduled Job")
            train_scheduled_job(on_openshift)
        except IOError:
            print("Another Instance is already working")
