from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.db import models
import datetime
import os
import sys
import json

# sys.path.append(settings.BASE_DIR+'/essay/classifier')


def get_File_Name(self, filename):
        now = datetime.datetime.now()
        return 'train_file/'+self.name.lower()+'/'+str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+'/'+filename


class EssayModel(models.Model):
    update_status = (
            ('0', 'no'),
            ('1', 'yes')
            )
    name = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(User, related_name='essayModels', null=True)
    info = models.CharField(max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    train_file = models.FileField(upload_to=get_File_Name)
    model_file = models.CharField(max_length=215, blank=True)
    train_len = models.IntegerField()
    train_file_updated = models.CharField(max_length=1, choices=update_status,
                                          default='1', blank=True)

    def __str__(self):
        return str(self.id)+': '+self.name

    # to check if name is unique insensitive
    def clean(self):
        self.name = self.name.lower()

    # def save(self, *args, **kwargs):
        # self.generate_model()
        # return super(EssayModel, self).save(*args, **kwargs)
    def evalute(self, essay_text):
        sys.path.append(settings.BASE_DIR+'/essay/classifier')
        from model import load_from_file
        name = self.name.lower()
        _model = load_from_file(os.path.join(settings.MEDIA_ROOT, 'model_file',
                               name, self.model_file, name))
        t = _model.predict([essay_text.split()])[0]
        return t

    def graph_data_save(self, field, value):
        model_directory = os.path.join(settings.MEDIA_ROOT,'model_file',
                                       self.name.lower(), self.model_file)
        _data_file = os.path.join(model_directory, 'data_file.json')
        data = {}
        try:
            data_file = open(_data_file, 'r')
            data = json.loads(data_file.read())
            data[field] = value
            data_file.close()
            data_file = open(_data_file, 'w')
        except (FileNotFoundError, ValueError) as e :
            data_file = open(_data_file, 'w')
            data[field] = value
        data_file.write(json.dumps(data))
        data_file.close()

    def graph_data_read(self, field):
        model_directory = os.path.join(settings.MEDIA_ROOT,'model_file',
                                       self.name.lower(), self.model_file)
        _data_file = os.path.join(model_directory, 'data_file.json')
        try:
            data_file = open(_data_file, 'r')
            data = json.loads(data_file.read())
            if field in data:
                return data.get(field)
            else:
                return None
        except (FileNotFoundError, ValueError) as e :
            return None


class CronJob(models.Model):
    CRONSTATUS = (
            ('0', 'pending'),
            ('1', 'running'),
            ('2', 'finished'),
            ('3', 'error'),
            )
    essaymodel = models.OneToOneField(EssayModel, unique=True,
                                      related_name='cronjob')
    status = models.CharField(max_length=1, choices=CRONSTATUS, default='0')
    updated = models.DateTimeField(auto_now=True)
    train_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        return str(self.id)+': CornJob('\
                +self.essaymodel.name+'[id:'+str(self.essaymodel.id)+'],'\
                +self.get_status_display()+')'

    def getStatus(self):
        return self.CRONSTATUS[int(self.status)][1]

    def train(self):
        sys.path.append(settings.BASE_DIR+'/essay/classifierNew')
        now = datetime.datetime.now()
        self.model_file = str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)
        self.status = '1'
        self.save()
        # try:
        essaymodel = EssayModel.objects.get(pk=self.essaymodel.pk)
        from model import EssayModel as esyModel
        from openpyxl import load_workbook
        from cbfs import Cbfs
        os.chdir(settings.BASE_DIR+'/essay/classifierNew/')
        file_location = essaymodel.train_file
        model_directory = os.path.join(settings.MEDIA_ROOT,'model_file',
                                       essaymodel.name.lower())
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
        test_essay = essay[:train_len]
        test_score = score[:train_len]
        # test_essay = essay[train_len:]
        # test_score = score[train_len:]
        mins = min(score)
        maxs = max(score)
        # from model import load_from_file
        # name = essaymodel.name.lower()
        # model = load_from_file(os.path.join(settings.MEDIA_ROOT,
                                # 'model_file', name,
                                # essaymodel.model_file,name))
        sk = True
        if sk:
            from sklearn import svm
            mod = svm.SVC(kernel = 'linear', decision_function_shape='ovo')
        else:
            import msvm
            mod = msvm.MSVM()
        feature = Cbfs()
        model = esyModel(mod, feature)
        model.train(train_essay, train_score, mins, maxs)
        model.score(test_essay, test_score)
        if not os.path.exists(model_directory+'/'+model_name):
            os.makedirs(model_directory+'/'+model_name)
        model.dump(model_directory+'/'+model_name+'/'+essaymodel.name.lower())
        print("Model dumped\n")
        # Evaluation of Model
        from grammar.evaluate import Evaluate
        ev = Evaluate()
        ev.calc_confusion(model.target, model.predicted, 2, 12)
        ev.ROC_parameters()
        essaymodel.graph_data_save('confusion', ev.confusion.tolist())
        essaymodel.graph_data_save('roc', ev.roc)
        essaymodel.graph_data_save('histogram', avg_mark_histogram(model.target,
                                                                   model.predicted))
        print("confusion and roc saved")

        # Word Cloud Generation
        from wordcloud import WordCloud
        bagofwords = model.ftransform.bagcount
        bagofwords = tuple(bagofwords.items())
        wc = WordCloud(min_font_size=10, background_color='white',
                       width=int(1920/2),height=int(1080/2))
        wc.generate_from_frequencies(bagofwords)
        wc.to_file(os.path.join(model_directory, model_name,'wordcloud.png'))
        print("wordcloud drawn")
        self.status = '2'
        self.save()

        # except Exception as e:
            # print(e)
            # self.status = '3'
            # self.save()


@receiver(pre_save, sender=EssayModel)
def pre_generate_model(sender, **kwargs):
    update = True
    essaymodel = kwargs['instance']
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


class Essay(models.Model):
    evalute_status = (
            ('0', 'no'),
            ('1', 'yes')
            )
    user = models.ForeignKey(User, related_name='essays', null=True)
    essaymodel = models.ForeignKey(EssayModel, related_name='essays')
    text = models.CharField(max_length=3000)
    predicted_mark = models.IntegerField(blank=True, null=True)
    original_mark = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    evalute_status = models.CharField(max_length=1, choices=evalute_status,
                                              default='0', blank=True)
    evalute_duration = models.DurationField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    grammar = models.IntegerField(blank=True, null=True)
    spell = models.IntegerField(blank=True, null=True)


    class Meta:
        # unique_together = (('user', 'essaymodel', 'text'))
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)+'Model: '+self.essaymodel.name+', User:\
               '+str(self.user.pk)+', O_mark,P_mark: ('+str(self.original_mark)+',\
               '+str(self.predicted_mark)+')'

def avg_mark_histogram(original, predicted):
    from collections import defaultdict
    zipped = zip(original, predicted)
    data = defaultdict(list)
    for ori, pred in list(zipped):
        data[ori].append(int(pred))
    return data
