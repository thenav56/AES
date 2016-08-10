from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.db import models
import datetime
import sys

sys.path.append(settings.BASE_DIR+'/essay/classifier')


def get_File_Name(self, filename):
        now = datetime.datetime.now()
        return 'train_file/'+self.name.lower()+'/'+str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+'/'+filename


class EssayModel(models.Model):
    update_status = (
            ('0', 'no'),
            ('1', 'yes')
            )
    name = models.CharField(max_length=200, unique=True)
    info = models.CharField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    train_file = models.FileField(upload_to=get_File_Name)
    model_file = models.CharField(max_length=215, blank=True)
    train_len = models.IntegerField()
    train_file_updated = models.CharField(max_length=1, choices=update_status, default='1')

    def __str__(self):
        return str(self.id)+': '+self.name

    # to check if name is unique insensitive
    def clean(self):
        self.name = self.name.lower()

    # def save(self, *args, **kwargs):
        # self.generate_model()
        # return super(EssayModel, self).save(*args, **kwargs)
    def evalute(self, essay_text):
        from model import load_from_file
        name = self.name.lower()
        model = load_from_file(settings.MEDIA_ROOT+'/model_file/'+name+'/'+self.model_file+'/'+name)
        t = model.predict([essay_text.split()])[0]
        return t


class CronJob(models.Model):
    CRONSTATUS = (
            ('0', 'pending'),
            ('1', 'running'),
            ('2', 'finished'),
            ('3', 'error'),
            )
    essaymodel = models.OneToOneField(EssayModel, unique=True)
    status = models.CharField(max_length=1, choices=CRONSTATUS, default='0')
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)+': CornJob('\
                +self.essaymodel.name+'[id:'+str(self.essaymodel.id)+'],'\
                +self.get_status_display()+')'

    def getStatus(self):
        return self.CRONSTATUS[int(self.status)][1]

    def train(self):
        self.status = '1'
        self.save()
        # try:
        essaymodel = EssayModel.objects.get(pk=self.essaymodel.pk)
        from model import EssayModel as esyModel
        from openpyxl import load_workbook
        import os
        os.chdir(settings.BASE_DIR+'/essay/classifier/')
        file_location = essaymodel.train_file
        model_directory = settings.MEDIA_ROOT+'/model_file/'+essaymodel.name.lower()
        model_name = essaymodel.model_file
        wb = load_workbook(file_location)
        ws = wb.active
        data = [[j.value for j in i] for i in ws]
        data = list(zip(*data))
        essay = data[2][1:]
        score = data[6][1:]
        train_len = int(essaymodel.train_len)  # training set size
        train_essay = essay[:train_len]
        train_score = score[:train_len]
        test_essay = essay[train_len:]
        # test_score = score[train_len:]
        train_essay = [i.split() for i in train_essay]
        test_essay = [i.split() for i in test_essay]
        # model = load_from_file('c2.model')
        model = esyModel(settings.BASE_DIR +
                         '/essay/classifier/cspell/files/big.txt')
        model.train(train_essay, train_score)
        if not os.path.exists(model_directory+'/'+model_name):
            os.makedirs(model_directory+'/'+model_name)
        model.dump(model_directory+'/'+model_name+'/'+essaymodel.name.lower())
        print("Model dumped\n")
        self.status = '2'
        self.save()
        # except:
            # self.status = '3'
            # self.save()



@receiver(pre_save, sender=EssayModel)
def pre_generate_model(sender, **kwargs):
    now = datetime.datetime.now()
    update = True
    essaymodel = kwargs['instance']
    essaymodel.model_file = str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)
    if essaymodel.pk is not None:
        if essaymodel.train_file_updated != '1':
            try:
                orig = EssayModel.objects.get(pk=essaymodel.pk)
                if orig.train_file == essaymodel.train_file:
                    update = False
            except EssayModel.DoesNotExist:
                update = True
    essaymodel.train_file_updated = '1' if update else '0'


@receiver(post_save, sender=EssayModel)
def post_generate_model(sender, **kwargs):
    essaymodel = kwargs['instance']
    if essaymodel.train_file_updated == '1':
        try:
            cronjob = CronJob.objects.get(essaymodel=essaymodel)
            cronjob.status = '0'
        except CronJob.DoesNotExist:
            cronjob = CronJob(essaymodel=essaymodel)
        cronjob.save()
