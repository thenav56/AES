import os
import time
import datetime


def evalute_essay_text():
    import django
    import sys

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    django.setup()
    from django.conf import settings

    sys.path.append(settings.BASE_DIR+'/essay/classifierNew')
    from model import load_from_file

    from essay.models import Essay, EssayModel
    models = {}
    essayModels = EssayModel.objects.all()
    while 1:
        for essayModel in essayModels:
            model = models.get(essayModel.pk, False)
            if model is False:
                name = essayModel.name.lower()
                model_start_t = time.time()
                model = load_from_file(os.path.join(settings.MEDIA_ROOT, 'model_file',
                                       name, essayModel.model_file, name))
                model_end_t = time.time()
                models.update({essayModel.pk: model})
                print('-------------------')
                print('Loaded %s into memory' % (essayModel.name) )
                print("Total Time To Load: ", (model_end_t-model_start_t))
                print('-------------------')
            try:
                essay = Essay.objects.order_by('updated').filter(essaymodel=essayModel,
                                                                 evalute_status='0')[0]
                if essay is not None:
                    print('-------------------')
                    start_t = time.time()
                    start_time = datetime.datetime.now()

                    print("Evalute Essay(pk=%s) for essayModel( %s )" % (essay.pk,
                          essay.essaymodel))

                    score = model.predict([essay.text])[0]
                    grammar = model.ftransform.gvalue
                    spell = model.ftransform.svalue

                    end_t = time.time()
                    end_time = datetime.datetime.now()
                    total_time = end_time - start_time
                    print('grammer: ',int(grammar*100), ' spell: ',
                          int(spell*100))
                    print("Total Time To Evaluate: ", (end_t-start_t))
                    print("Started At :", start_time)
                    print("AND Ended At :", end_time)
                    print('-------------------')

                    essay.evalute_duration = total_time
                    essay.predicted_mark = score
                    essay.grammar = int(grammar*100)
                    essay.spell = int(spell*100)
                    essay.evalute_status = '1'
                    essay.save()
            except IndexError:
                print("Empty Essay queue")
                time.sleep(5)

if __name__ == "__main__":
    evalute_essay_text()
