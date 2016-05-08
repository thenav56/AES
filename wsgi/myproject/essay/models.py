from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import models
import datetime
import sys

sys.path.append(settings.BASE_DIR+'/essay/classifier')
now = datetime.datetime.now()


def get_File_Name(self, filename):
        return 'train_file/'+self.name.lower()+'/'+str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+'/'+filename


class EssayModel(models.Model):
    name = models.CharField(max_length=200, unique=True)
    info = models.CharField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    train_file = models.FileField(upload_to=get_File_Name)
    model_file = models.CharField(max_length=215, blank=True)
    train_len = models.IntegerField()

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
        model = load_from_file(settings.MEDIA_ROOT+'/train_file/'+self.name+'/'+essayModel.model_file+'/'+essayModel.name)
        t = model.predict([essay_text.split()])[0]
        return t


@receiver(pre_save, sender=EssayModel)
def generate_model(sender, **kwargs):
    update = True
    if kwargs['instance'].pk is not None:
        try:
            orig = EssayModel.objects.get(pk=kwargs['instance'].pk)
            if orig.train_file == kwargs['instance'].train_file:
                update = False
        except EssayModel.DoesNotExist:
            update = True
    if update:
        kwargs['instance'].model_file = str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+'/'
        from model import EssayModel as esyModel
        from openpyxl import load_workbook
        import os
        os.chdir(settings.BASE_DIR+'/essay/classifier/')
        file_location = kwargs['instance'].train_file
        model_directory = settings.MEDIA_ROOT+'/train_file/'+kwargs['instance'].name
        model_name = kwargs['instance'].model_file
        wb = load_workbook(file_location)
        ws = wb.active
        data = [[j.value for j in i] for i in ws]
        data = list(zip(*data))
        essay = data[2][1:]
        score = data[6][1:]
        train_len = int(kwargs['instance'].train_len)  # training set size
        train_essay = essay[:train_len]
        train_score = score[:train_len]
        test_essay = essay[train_len:]
        # test_score = score[train_len:]
        train_essay = [i.split() for i in train_essay]
        test_essay = [i.split() for i in test_essay]
        # model = load_from_file('c2.model')
        model = esyModel(settings.BASE_DIR+'/essay/classifier/cspell/files/big.txt')
        model.train(train_essay, train_score)
        if not os.path.exists(model_directory+'/'+model_name):
            os.makedirs(model_directory+'/'+model_name)
        model.dump(model_directory+'/'+model_name+kwargs['instance'].name.lower())
        print("Model dumped\n")
