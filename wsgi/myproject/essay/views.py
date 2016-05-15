from django.shortcuts import render
from django.http import Http404

from .models import EssayModel, CronJob
# from .forms import DocumentForm


def index(request):
    essaysets = EssayModel.objects.all()
    context = {
            'essaysets': essaysets
            }
    return render(request, 'essay/index.html', context)


def register(request):
    if request.method == 'GET':
        return render(request, 'essay/register.html')
    elif request.method == 'POST':
        name = request.POST.get('name')
        info = request.POST.get('info')
        train_file = request.FILES['train_file']
        train_len = request.POST.get('train_len')
        essayModel = EssayModel(name=name, info=info,
                                train_file=train_file, train_len=train_len)
        essayModel.save()
        context = {
                'flash': True,
                'success': True
                }
        # context = {
                # 'flash': True,
                # 'success': False
                # }
        return render(request, 'essay/register.html', context)


def view(request, essayModel_id):
    try:
        essayModel = EssayModel.objects.get(pk=essayModel_id)
        cronjob = CronJob.objects.get(essaymodel=essayModel)
        cronjobStatus = cronjob.getStatus()
        context = {
                'essayModel': essayModel,
                'autofocus': 'autofocus',
                'cronjobStatus': cronjobStatus
                }
        if request.method == 'POST':
            essay_text = request.POST.get('essay_text')
            t = essayModel.evalute(essay_text)
            alert = "alert-success" if t >= 4.8 else "alert-warning"
            scored_position = "Nice Work" if t >= 4.8 else "Need More Effort"
            context.update({
                    'flash': True,
                    'marks_scored': t,
                    'alert': alert,
                    'scored_position': scored_position,
                    'essay_text': essay_text,
                    'autofocus': ''
                    })
    except EssayModel.DoesNotExist:
        raise Http404("Essay Model does not Exist")
    return render(request, 'essay/detail.html', context)
