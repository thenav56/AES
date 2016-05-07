from django.shortcuts import render
from django.http import Http404

from .models import EssayModel
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
        try:
            name = request.POST.get('name')
            info = request.POST.get('info')
            train_file = request.FILES['train_file']
            essayModel = EssayModel(name=name, info=info,
                                    train_file=train_file)
            essayModel.save()
            context = {
                    'flash': True,
                    'success': True
                    }
        except:
            context = {
                    'flash': True,
                    'success': False
                    }
        return render(request, 'essay/register.html', context)


def view(request, essayModel_id):
    try:
        essayModel = EssayModel.objects.get(pk=essayModel_id)
        context = {
                'essayModel': essayModel,
                'autofocus': 'autofocus'
                }
        if request.method == 'POST':
            essay_text = request.POST.get('essay_text')
            import sys
            from django.conf import settings
            sys.path.append(settings.BASE_DIR+'/classifier/')
            from model import load_from_file
            model = load_from_file(settings.BASE_DIR+'/media/train_file/'+essayModel.name+'/'+essayModel.model_file+'/'+essayModel.name)
            t = model.predict([essay_text.split()])[0]
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
